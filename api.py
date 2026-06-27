from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

# Supported regions based on your preferences (IN, BD, PK, NA, SG)
# You can extend this dictionary with region-specific configurations if needed
REGION_CONFIG = {
    'IND': {'region_code': 'IN', 'language': 'en', 'source': 'mb'},
    'BD': {'region_code': 'BD', 'language': 'en', 'source': 'mb'},
    'PK': {'region_code': 'PK', 'language': 'en', 'source': 'mb'},
    'NA': {'region_code': 'NA', 'language': 'en', 'source': 'mb'},
    'SG': {'region_code': 'SG', 'language': 'en', 'source': 'mb'},
}

@app.route('/check', methods=['GET'])
def check_player():
    target_id = request.args.get('uid')
    region = request.args.get('region', 'IND').upper()  # Default to IN if not provided
    
    if not target_id:
        return jsonify({"message": "Missing 'uid' parameter Please give a valid uid !!"}), 400
    
    if region not in REGION_CONFIG:
        return jsonify({"ServerError": f"Unsupported region: ({region}) please give any valid region like - {', '.join(REGION_CONFIG.keys())}"}), 400
    
    # Get region-specific config
    config = REGION_CONFIG[region]
    
    # Base cookies (updated to be more generic; you may need to refresh session_key and datadome periodically)
    cookies = {
            '_ga': 'GA1.1.2123120599.1674510784',
            '_fbp': 'fb.1.1674510785537.363500115',
            '_ga_7JZFJ14B0B': 'GS1.1.1674510784.1.1.1674510789.0.0.0',
            'source': 'mb',
            'region': 'MA',
            'language': 'ar',
            '_ga_TVZ1LG7BEB': 'GS1.1.1674930050.3.1.1674930171.0.0.0',
            'datadome': '6h5F5cx_GpbuNtAkftMpDjsbLcL3op_5W5Z-npxeT_qcEe_7pvil2EuJ6l~JlYDxEALeyvKTz3~LyC1opQgdP~7~UDJ0jYcP5p20IQlT3aBEIKDYLH~cqdfXnnR6FAL0',
            'session_key': 'efwfzwesi9ui8drux4pmqix4cosane0y',
    }

    headers = {
            'Accept-Language': 'en-US,en;q=0.9',
            'Connection': 'keep-alive',
            'Origin': 'https://shop2game.com',
            'Referer': 'https://shop2game.com/app/100067/idlogin',
            'User-Agent': 'Mozilla/5.0 (Linux; Android 11; Redmi Note 8) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Mobile Safari/537.36',
            'accept': 'application/json',
            'content-type': 'application/json',
            'sec-ch-ua': '"Chromium";v="107", "Not=A?Brand";v="24"',
            'sec-ch-ua-mobile': '?1',
            'sec-ch-ua-platform': '"Android"',
            'x-datadome-clientid': '6h5F5cx_GpbuNtAkftMpDjsbLcL3op_5W5Z-npxeT_qcEe_7pvil2EuJ6l~JlYDxEALeyvKTz3~LyC1opQgdP~7~UDJ0jYcP5p20IQlT3aBEIKDYLH~cqdfXnnR6FAL0',
    }

    json_data = {
        'app_id': 100067,
        'login_id': target_id,
        'app_server_id': 0,
    }

    try:
        res = requests.post('https://shop2game.com/api/auth/player_id_login', cookies=cookies, headers=headers, json=json_data)
        res.raise_for_status()  # Raise error for non-200 status
        
        player_data = res.json()
        if not player_data.get('nickname'):
            return jsonify({"Error":  f"UID ({target_id}) IS NOT FOUND IN ({region}) 🚫" }), 404

        nickname = player_data.get('nickname', 'N/A')
        retrieved_region = player_data.get('region', 'N/A')
        account_id = request.args.get('uid')

        # Ban check
        ban_url = f'https://ff.garena.com/api/antihack/check_banned?lang=en&uid={target_id}&region={region}'
        ban_response = requests.get(ban_url, headers={
                'User-Agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36',
                'Accept': 'application/json, text/plain, */*',
                'authority': 'ff.garena.com',
                'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8',
                'referer': 'https://ff.garena.com/en/support/',
                'sec-ch-ua': '"Not_A Brand";v="8", "Chromium";v="120"',
                'sec-ch-ua-mobile': '?1',
                'sec-ch-ua-platform': '"Android"',
                'sec-fetch-dest': 'empty',
                'sec-fetch-mode': 'cors',
                'sec-fetch-site': 'same-origin',
                'x-requested-with': 'B6FksShzIgjfrYImLpTsadjS86sddhFH',
        })
        ban_response.raise_for_status()
        
        ban_data = ban_response.json()
        is_banned = False
        ban_period = 0
        if ban_data.get("status") == "success" and "data" in ban_data:
            is_banned = bool(ban_data["data"].get("is_banned", 0))
            period = int(ban_data["data"].get("period", 0))
            ban_period_msg = f"{period} months" if is_banned and period > 0 else None
            ban_status = "Banned ⛔" if is_banned else "Not Banned ✅"

        return jsonify({
            "nickname": nickname,
            "region": retrieved_region,
            "is_banned": ban_status,
            "ban_period": ban_period_msg,
            "uid": account_id,
        })
    except requests.exceptions.RequestException as e:
        return jsonify({"message": f"Request failed: {str(e)}"}), 500
    except ValueError as e:
        return jsonify({ "message": f"Invalid response: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(debug=True)
