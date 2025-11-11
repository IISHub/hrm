def mock_get_by_nrc(nrc):
    data = {
        "statusCode": 200,
        "data": {
            "firstName": "John",
            "lastName": "Doe",
            "nrc": nrc,
            "ssn": "SSN123456"
        }
    }

    print(data)
    return data

def mock_get_member_by_ssn(ssn):
    
    data = {
        "statusCode": 200,
        "data": {
          
            "firstName": "John",
            "lastName": "Doe",
            "nrc": "987654/32/1",
            "ssn": ssn
        }
    }

    print(data)
    return data