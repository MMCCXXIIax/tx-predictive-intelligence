export async function saveProfile({
  id,
  name,
  email,
  mode = "demo",
}: {
  id: string
  name: string
  email: string
  mode?: "demo" | "live"
}) {
  try {
    const res = await fetch("/api/save-profile", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ id, name, email, mode }),
    })

    const data = await res.json()

    if (!res.ok || data.status !== "ok") {
      throw new Error(data.message || "Save failed")
    }

    return { success: true }
  } catch (err) {
    console.error("❌ Failed to save profile:", err)
    return { success: false, error: err.message }
  }
}
