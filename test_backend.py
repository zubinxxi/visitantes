import asyncio
import httpx

async def test_users_endpoint():
    # 1. Login to get token
    async with httpx.AsyncClient() as client:
        login_res = await client.post("http://localhost:8000/api/v1/auth/login", json={
            "login": "sysadmin",
            "password": "123456"
        })
        if login_res.status_code != 200:
            print(f"Login failed: {login_res.status_code} {login_res.text}")
            return
        
        data = login_res.json()
        token = data["access_token"]
        print(f"Login successful. Admin: {data['user']['priv_admin']}")
        
        # 2. Call users endpoint
        users_res = await client.get("http://localhost:8000/api/v1/maintenance/users/", headers={
            "Authorization": f"Bearer {token}"
        })
        print(f"Users endpoint: {users_res.status_code} {users_res.text}")

        # 3. Call permissions endpoint
        perms_res = await client.get("http://localhost:8000/api/v1/security/me/permissions", headers={
            "Authorization": f"Bearer {token}"
        })
        print(f"Permissions endpoint: {perms_res.status_code} {perms_res.text}")

if __name__ == "__main__":
    asyncio.run(test_users_endpoint())
