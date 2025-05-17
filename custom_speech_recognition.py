import http.client
import json

# Function for Alibaba Cloud Short Sentence Recognition
def recognize_speech_from_bytes(audio_bytes, app_key, token, input_format='pcm', sample_rate=16000):
    host = 'nls-gateway-ap-southeast-1.aliyuncs.com'
    url = 'http://nls-gateway-ap-southeast-1.aliyuncs.com/stream/v1/asr'

    # Configure the RESTful request parameters.
    request_url = url + '?appkey=' + app_key
    request_url += '&format=' + input_format # Use passed format
    request_url += '&sample_rate=' + str(sample_rate) # Use passed sample rate
    request_url += '&enable_punctuation_prediction=true'
    request_url += '&enable_inverse_text_normalization=true'
    # request_url += '&enable_voice_detection=false' # Optional

    http_headers = {
        'X-NLS-Token': token,
        'Content-type': 'application/octet-stream',
        'Content-Length': len(audio_bytes)
    }

    try:
        conn = http.client.HTTPConnection(host)
        conn.request(method='POST', url=request_url, body=audio_bytes, headers=http_headers)
        response = conn.getresponse()
        
        response_body = response.read()
        conn.close()

        if response.status == 200:
            try:
                body_json = json.loads(response_body)
                if body_json.get('status') == 20000000:
                    return body_json.get('result'), None
                else:
                    error_message = f"Recognizer failed: {body_json.get('status')} - {body_json.get('message', 'No message')}"
                    return None, error_message
            except json.JSONDecodeError:
                return None, "The response is not json format string"
            except ValueError: # Redundant with JSONDecodeError but kept for safety from original
                return None, "The response is not json format string (ValueError)"
        else:
            return None, f"HTTP Error: {response.status} {response.reason}. Response: {response_body.decode(errors='ignore')}"

    except Exception as e:
        return None, f"An error occurred during speech recognition: {str(e)}" 