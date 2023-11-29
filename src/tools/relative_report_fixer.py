import json

def __main(report_path: str) -> None:
    content = ""
    with open(report_path, 'r') as file:
        content = file.read()

    report = json.loads(content)
    for err in report:
        filename = err['filename'].split('src')

        err['filename'] = f'/github/workspace/src{filename[1]}'
        print(err['filename'])
    with open(report_path, 'w') as file:
        file.write(json.dumps(report))

if __name__=='__main__':
    __main('ruff_report.json')