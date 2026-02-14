import requests

try:
    r = requests.post('http://127.0.0.1:8000/visits', json={
        'age': 55,
        'gender': 'Male',
        'systolic_bp': 160,
        'heart_rate': 110,
        'temperature': 38.5,
        'symptoms': ['chest pain', 'shortness of breath'],
        'chronic_conditions': ['hypertension', 'diabetes'],
        'visit_type': 'Walk-In'
    })
    print(f"Status: {r.status_code}")
    # Write full response to file
    with open('error_detail.txt', 'w') as f:
        f.write(r.text)
    print("Full response written to error_detail.txt")
except Exception as e:
    print(f"Error: {e}")
