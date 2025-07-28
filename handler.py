import runpod

def handler(event):
    return {"message": "Working!", "input": event.get("input", {})}

if __name__ == '__main__':
    runpod.serverless.start({'handler': handler})
