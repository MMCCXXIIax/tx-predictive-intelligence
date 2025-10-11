"""
Reinforcement Learning Trading Agent
Optimizes entry/exit timing using Deep Q-Learning (DQN)
Learns optimal actions: BUY, SELL, HOLD based on market state
"""

import os
import logging
import pickle
import random
from collections import deque
from typing import Dict, Any, List, Tuple, Optional
from dataclasses import dataclass
from enum import Enum

import numpy as np
import pandas as pd

# RL libraries
try:
    import torch
    import torch.nn as nn
    import torch.optim as optim
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False
    logging.warning("PyTorch not available. RL agent disabled.")

logger = logging.getLogger(__name__)


class TradingAction(Enum):
    """Trading actions"""
    HOLD = 0
    BUY = 1
    SELL = 2


@dataclass
class TradingState:
    """Market state representation"""
    price: float
    volume: float
    rsi: float
    macd: float
    bb_position: float
    sentiment: float
    position: int  # 0=no position, 1=long, -1=short
    pnl: float
    time_in_position: int


@dataclass
class Experience:
    """Experience tuple for replay buffer"""
    state: np.ndarray
    action: int
    reward: float
    next_state: np.ndarray
    done: bool


class DQNetwork(nn.Module):
    """Deep Q-Network for action-value estimation"""
    
    def __init__(self, state_dim: int, action_dim: int, hidden_dims: List[int] = [128, 64]):
        super(DQNetwork, self).__init__()
        
        layers = []
        prev_dim = state_dim
        
        for hidden_dim in hidden_dims:
            layers.append(nn.Linear(prev_dim, hidden_dim))
            layers.append(nn.ReLU())
            layers.append(nn.Dropout(0.2))
            prev_dim = hidden_dim
        
        layers.append(nn.Linear(prev_dim, action_dim))
        
        self.network = nn.Sequential(*layers)
    
    def forward(self, state):
        return self.network(state)


class ReplayBuffer:
    """Experience replay buffer for DQN"""
    
    def __init__(self, capacity: int = 10000):
        self.buffer = deque(maxlen=capacity)
    
    def push(self, experience: Experience):
        self.buffer.append(experience)
    
    def sample(self, batch_size: int) -> List[Experience]:
        return random.sample(self.buffer, min(batch_size, len(self.buffer)))
    
    def __len__(self):
        return len(self.buffer)


class RLTradingAgent:
    """
    Reinforcement Learning agent for optimal entry/exit timing
    Uses Double DQN with experience replay
    """
    
    def __init__(self, state_dim: int = 9, action_dim: int = 3, 
                 model_dir: str = 'models/rl_agent'):
        self.state_dim = state_dim
        self.action_dim = action_dim
        self.model_dir = model_dir
        os.makedirs(model_dir, exist_ok=True)
        
        # Hyperparameters
        self.gamma = 0.99  # Discount factor
        self.epsilon = 1.0  # Exploration rate
        self.epsilon_min = 0.01
        self.epsilon_decay = 0.995
        self.learning_rate = 0.001
        self.batch_size = 64
        self.target_update_freq = 10
        
        # Networks
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        
        if TORCH_AVAILABLE:
            self.policy_net = DQNetwork(state_dim, action_dim).to(self.device)
            self.target_net = DQNetwork(state_dim, action_dim).to(self.device)
            self.target_net.load_state_dict(self.policy_net.state_dict())
            self.target_net.eval()
            
            self.optimizer = optim.Adam(self.policy_net.parameters(), lr=self.learning_rate)
            self.criterion = nn.MSELoss()
        
        # Replay buffer
        self.replay_buffer = ReplayBuffer(capacity=10000)
        
        # Training metrics
        self.episode_rewards = []
        self.episode_count = 0
        
        # Load existing model if available
        self._load_model()
    
    def _load_model(self):
        """Load saved model if exists"""
        model_path = os.path.join(self.model_dir, 'dqn_model.pth')
        if os.path.exists(model_path) and TORCH_AVAILABLE:
            try:
                self.policy_net.load_state_dict(torch.load(model_path, map_location=self.device))
                self.target_net.load_state_dict(self.policy_net.state_dict())
                logger.info("RL agent model loaded successfully")
            except Exception as e:
                logger.error(f"Failed to load RL model: {e}")
    
    def _save_model(self):
        """Save current model"""
        if not TORCH_AVAILABLE:
            return
        
        model_path = os.path.join(self.model_dir, 'dqn_model.pth')
        try:
            torch.save(self.policy_net.state_dict(), model_path)
            logger.info("RL agent model saved")
        except Exception as e:
            logger.error(f"Failed to save RL model: {e}")
    
    def state_to_array(self, state: TradingState) -> np.ndarray:
        """Convert TradingState to numpy array"""
        return np.array([
            state.price / 1000.0,  # Normalize
            state.volume / 1e6,
            state.rsi / 100.0,
            state.macd,
            state.bb_position,
            state.sentiment,
            float(state.position),
            state.pnl / 1000.0,
            state.time_in_position / 100.0
        ], dtype=np.float32)
    
    def select_action(self, state: TradingState, training: bool = False) -> TradingAction:
        """
        Select action using epsilon-greedy policy
        
        Args:
            state: Current market state
            training: If True, use exploration; if False, use exploitation only
        
        Returns:
            TradingAction
        """
        if not TORCH_AVAILABLE:
            return TradingAction.HOLD
        
        # Epsilon-greedy exploration
        if training and random.random() < self.epsilon:
            return TradingAction(random.randint(0, self.action_dim - 1))
        
        # Exploitation: choose best action
        state_array = self.state_to_array(state)
        state_tensor = torch.FloatTensor(state_array).unsqueeze(0).to(self.device)
        
        with torch.no_grad():
            q_values = self.policy_net(state_tensor)
            action_idx = q_values.argmax().item()
        
        return TradingAction(action_idx)
    
    def calculate_reward(self, prev_state: TradingState, action: TradingAction,
                        next_state: TradingState) -> float:
        """
        Calculate reward for taking action in state
        
        Reward components:
        - PnL change (primary)
        - Penalty for excessive trading
        - Bonus for holding winning positions
        - Penalty for holding losing positions too long
        """
        # PnL change
        pnl_change = next_state.pnl - prev_state.pnl
        reward = pnl_change * 10.0  # Scale up
        
        # Penalty for excessive trading (encourage patience)
        if action != TradingAction.HOLD:
            reward -= 0.1
        
        # Bonus for holding winning positions
        if next_state.position != 0 and next_state.pnl > 0:
            reward += 0.05
        
        # Penalty for holding losing positions too long
        if next_state.position != 0 and next_state.pnl < 0 and next_state.time_in_position > 20:
            reward -= 0.1
        
        # Large penalty for big losses
        if pnl_change < -5.0:
            reward -= 5.0
        
        # Large bonus for big wins
        if pnl_change > 5.0:
            reward += 5.0
        
        return reward
    
    def train_step(self):
        """Perform one training step using experience replay"""
        if not TORCH_AVAILABLE or len(self.replay_buffer) < self.batch_size:
            return
        
        # Sample batch
        experiences = self.replay_buffer.sample(self.batch_size)
        
        states = torch.FloatTensor([exp.state for exp in experiences]).to(self.device)
        actions = torch.LongTensor([exp.action for exp in experiences]).to(self.device)
        rewards = torch.FloatTensor([exp.reward for exp in experiences]).to(self.device)
        next_states = torch.FloatTensor([exp.next_state for exp in experiences]).to(self.device)
        dones = torch.FloatTensor([exp.done for exp in experiences]).to(self.device)
        
        # Current Q values
        current_q_values = self.policy_net(states).gather(1, actions.unsqueeze(1)).squeeze()
        
        # Target Q values (Double DQN)
        with torch.no_grad():
            next_actions = self.policy_net(next_states).argmax(1)
            next_q_values = self.target_net(next_states).gather(1, next_actions.unsqueeze(1)).squeeze()
            target_q_values = rewards + (1 - dones) * self.gamma * next_q_values
        
        # Compute loss and update
        loss = self.criterion(current_q_values, target_q_values)
        
        self.optimizer.zero_grad()
        loss.backward()
        torch.nn.utils.clip_grad_norm_(self.policy_net.parameters(), 1.0)
        self.optimizer.step()
        
        return loss.item()
    
    def update_target_network(self):
        """Update target network with policy network weights"""
        if TORCH_AVAILABLE:
            self.target_net.load_state_dict(self.policy_net.state_dict())
    
    def train_episode(self, market_data: pd.DataFrame, initial_capital: float = 10000.0) -> Dict[str, Any]:
        """
        Train agent on one episode of market data
        
        Args:
            market_data: DataFrame with OHLCV and indicators
            initial_capital: Starting capital
        
        Returns:
            Episode statistics
        """
        if not TORCH_AVAILABLE or len(market_data) < 10:
            return {'success': False, 'error': 'Insufficient data or PyTorch unavailable'}
        
        capital = initial_capital
        position = 0
        entry_price = 0.0
        pnl = 0.0
        time_in_position = 0
        total_reward = 0.0
        actions_taken = []
        
        for i in range(len(market_data) - 1):
            row = market_data.iloc[i]
            next_row = market_data.iloc[i + 1]
            
            # Build state
            state = TradingState(
                price=row['close'],
                volume=row['volume'],
                rsi=row.get('rsi14', 50.0),
                macd=row.get('macd', 0.0),
                bb_position=row.get('bb_position', 0.5),
                sentiment=row.get('sentiment', 0.0),
                position=position,
                pnl=pnl,
                time_in_position=time_in_position
            )
            
            # Select action
            action = self.select_action(state, training=True)
            actions_taken.append(action.name)
            
            # Execute action
            if action == TradingAction.BUY and position == 0:
                position = 1
                entry_price = row['close']
                time_in_position = 0
            elif action == TradingAction.SELL and position == 1:
                pnl += (row['close'] - entry_price) / entry_price * 100
                position = 0
                time_in_position = 0
            
            if position == 1:
                time_in_position += 1
            
            # Next state
            next_state = TradingState(
                price=next_row['close'],
                volume=next_row['volume'],
                rsi=next_row.get('rsi14', 50.0),
                macd=next_row.get('macd', 0.0),
                bb_position=next_row.get('bb_position', 0.5),
                sentiment=next_row.get('sentiment', 0.0),
                position=position,
                pnl=pnl,
                time_in_position=time_in_position
            )
            
            # Calculate reward
            reward = self.calculate_reward(state, action, next_state)
            total_reward += reward
            
            # Store experience
            done = (i == len(market_data) - 2)
            experience = Experience(
                state=self.state_to_array(state),
                action=action.value,
                reward=reward,
                next_state=self.state_to_array(next_state),
                done=done
            )
            self.replay_buffer.push(experience)
            
            # Train
            self.train_step()
        
        # Update target network periodically
        self.episode_count += 1
        if self.episode_count % self.target_update_freq == 0:
            self.update_target_network()
        
        # Decay epsilon
        self.epsilon = max(self.epsilon_min, self.epsilon * self.epsilon_decay)
        
        # Save model periodically
        if self.episode_count % 50 == 0:
            self._save_model()
        
        self.episode_rewards.append(total_reward)
        
        return {
            'success': True,
            'episode': self.episode_count,
            'total_reward': total_reward,
            'final_pnl': pnl,
            'epsilon': self.epsilon,
            'actions': actions_taken,
            'buffer_size': len(self.replay_buffer)
        }
    
    def get_optimal_action(self, state: TradingState) -> Dict[str, Any]:
        """
        Get optimal action for current state (inference mode)
        
        Returns:
            Dict with action and Q-values
        """
        if not TORCH_AVAILABLE:
            return {'action': 'HOLD', 'confidence': 0.0}
        
        state_array = self.state_to_array(state)
        state_tensor = torch.FloatTensor(state_array).unsqueeze(0).to(self.device)
        
        with torch.no_grad():
            q_values = self.policy_net(state_tensor).cpu().numpy()[0]
        
        action_idx = q_values.argmax()
        action = TradingAction(action_idx)
        confidence = q_values[action_idx] / (q_values.sum() + 1e-8)
        
        return {
            'action': action.name,
            'confidence': float(confidence),
            'q_values': {
                'HOLD': float(q_values[0]),
                'BUY': float(q_values[1]),
                'SELL': float(q_values[2])
            }
        }


# Singleton instance
_rl_agent = None

def get_rl_agent() -> RLTradingAgent:
    """Get or create RL agent instance"""
    global _rl_agent
    if _rl_agent is None:
        _rl_agent = RLTradingAgent()
    return _rl_agent
