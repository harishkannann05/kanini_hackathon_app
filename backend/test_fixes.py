
import asyncio
import httpx

async def test_endpoints():
    async with httpx.AsyncClient(base_url="http://127.0.0.1:8000") as client:
        print("Testing GET /doctors...")
        r = await client.get("/doctors")
        if r.status_code == 200:
            data = r.json()
            if data and "full_name" in data[0]:
                print(f"SUCCESS: Found full_name in doctor response: {data[0]['full_name']}")
            else:
                print("FAILURE: 'full_name' missing in /doctors response")
                print(data[0] if data else "No doctors found")
        else:
            print(f"FAILURE: /doctors returned {r.status_code}")

        print("\nTesting GET /stats...")
        r = await client.get("/stats")
        if r.status_code == 200:
            data = r.json()
            recent = data.get("recent_visits", []) # recent_visits? Check key in main.py
            # wait, main.py returns dict with keys "risk_distribution", "department_load", "recent_visits". NO!
            # Let's check main.py return value.
            # line 298: return { "risk_distribution": ..., "department_load": ..., "recent_visits": recent }
            # Wait, line 298 was not fully visible. I assume "recent_visits" key.
            # In update, I saw `recent = [...]`.
            # I must check the return key.
            pass
        else:
            print(f"FAILURE: /stats returned {r.status_code}")

if __name__ == "__main__":
    asyncio.run(test_endpoints())
