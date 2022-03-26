import gspread
import json
import copy
import csv
import time


def setup():
    global sh
    global gc

    try:
        creds_file = open("credentials.json", "r")
        creds = json.load(creds_file)
        creds_file.close()
        gc = gspread.service_account(filename="credentials.json")
    except Exception as e:
        print(e)
        print(
            "Could not find credentials.json, make sure you have the file in the same directory as the exe, and named exactly 'credentials.json'"
        )
        input("")

    while True:
        try:
            print("Don't forget to share the google sheet with", creds["client_email"])
            link = input("Link to your Sheet:")
            sh = gc.open_by_url(link)
        except Exception as e:
            print(
                "Error occurred try again, you likely typed in the URL incorrectly or did not share it with the email"
            )
            print(e)
            continue
        else:
            break

    first_shs = setupFirstSheet()
    print("Finished setup")
    return first_shs


def setupFirstSheet():
    try:
        first_shs = sh.worksheet("First Strongholds")
        user_input = input("Do you want to keep these first strongholds? (y/n)\n")
        if user_input.lower() == "n":
            first_shs.resize(1, 2)
            first_shs.resize(9, 2)
            first_shs.update("A1:B1", [["x", "z"]])

    except:
        first_shs = sh.get_worksheet(0)
        first_shs.resize(9, 2)
        first_shs.update("A1:B1", [["x", "z"]])
        first_shs.update_title("First Strongholds")
    return first_shs


def createWorkSheet(name):
    try:
        ws = sh.worksheet(name)
        ws.resize(1)
    except:
        ws = sh.add_worksheet(title=name, rows="1", cols="2")
    ws.update("A1:B1", [["x", "z"]])
    return ws


def addData(data, sheet):
    sheet.append_row(data)


def getData(num_players):
    if num_players == 0:
        data = sh.get_worksheet(0).get_all_records()
        shs = []
        for d in data:
            shs.append([d["x"], d["z"]])
        return shs

    players = []
    for i in range(1, num_players + 1):
        try:
            data = sh.get_worksheet(i).get_all_records()
            player = []
            for d in data:
                player.append([d["x"], d["z"]])
            players.append(player)
        except:
            print("It appears you don't have a spreadsheet at index", i)


def main():
    try:

        scope = [
            "https://spreadsheets.google.com/feeds​",
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive.file​",
            "https://www.googleapis.com/auth/drive​",
        ]

        colorCell = "L2"

        # Setting up constants and verifying
        dataSheet = sh.worksheet("Raw Data")
        statsSheet = sh.worksheet("Stats")
        color = (15.0, 15.0, 15.0)
        if statsSheet.get(colorCell)[0][0] == "Gray":
            statsSheet.update(colorCell, "White")
            color = (1.0, 1.0, 1.0)
        else:
            statsSheet.update(colorCell, "Gray")
        global pushedLines
        pushedLines = 1
        cfgStartCol = "A"
        cfgStartRow = 6
        columns = int(statsSheet.get("B2")[0][0])
        rows = int(statsSheet.get("B3")[0][0])
        pushCol = statsSheet.get("D2")[0][0]
        pushRow = statsSheet.get("D3")[0][0]
        config = statsSheet.get(
            cfgStartCol
            + str(cfgStartRow)
            + ":"
            + chr(ord(cfgStartCol) + columns - 1)
            + str(cfgStartRow + rows - 1),
            value_render_option="FORMULA",
        )
        statsCsv = "stats.csv"

        def initialize_session():
            cfgStartCol = "A"

            cfgStartRow = 6
            columns = int(statsSheet.get("B2")[0][0])
            rows = int(statsSheet.get("B3")[0][0])
            pushCol = statsSheet.get("D2")[0][0]
            pushRow = statsSheet.get("D3")[0][0]

            init_config = getConfig(cell_list=False)

            statsSheet.insert_row([""], index=int(pushRow))
            statsSheet.insert_rows(
                init_config, row=int(pushRow), value_input_option="USER_ENTERED"
            )

            gc.request(
                "post",
                "https://sheets.googleapis.com/v4/spreadsheets/"
                + sh.id
                + ":batchUpdate",
                json={
                    "requests": [
                        {
                            "copyPaste": {
                                "source": {
                                    "sheetId": statsSheet.id,
                                    "startRowIndex": cfgStartRow - 1,
                                    "endRowIndex": cfgStartRow + rows - 1,
                                    "startColumnIndex": ord(cfgStartCol) - ord("A"),
                                    "endColumnIndex": ord(cfgStartCol)
                                    - ord("A")
                                    + columns,
                                },
                                "destination": {
                                    "sheetId": statsSheet.id,
                                    "startRowIndex": int(pushRow) - 1,
                                    "endRowIndex": int(pushRow) + rows - 1,
                                    "startColumnIndex": ord(pushCol) - ord("A"),
                                    "endColumnIndex": ord(pushCol) - ord("A") + columns,
                                },
                                "pasteType": "PASTE_FORMAT",
                                "pasteOrientation": "NORMAL",
                            }
                        }
                    ]
                },
            )

        def update_session():
            cell_list = getConfig()
            statsSheet.update_cells(cell_list, value_input_option="USER_ENTERED")

        def getConfig(cell_list=True):
            if cell_list:
                result = statsSheet.range(
                    pushCol
                    + str(pushRow)
                    + ":"
                    + chr(ord(pushCol) + columns - 1)
                    + str(int(pushRow) + rows - 1)
                )
            else:
                result = copy.deepcopy(config)

            config_copy = copy.deepcopy(config)
            config_copy[0][0].replace("~", str(pushedLines)).replace("'=", "=")
            for i in range(len(config_copy)):
                for j in range(len(config_copy[i])):
                    if type(config_copy[i][j] == str):
                        if cell_list:
                            result[(i * columns) + j].value = (
                                config_copy[i][j]
                                .replace("~", str(pushedLines))
                                .replace("'=", "=")
                            )
                        else:
                            result[i][j] = (
                                config_copy[i][j]
                                .replace("~", str(pushedLines))
                                .replace("'=", "=")
                            )
            return result

        def push_data():
            global pushedLines
            with open(statsCsv, newline="") as f:
                reader = csv.reader(f)
                data = list(reader)
                f.close()

            try:
                if len(data) == 0:
                    return
                # print(data)
                dataSheet.insert_rows(
                    data,
                    row=2,
                    value_input_option="USER_ENTERED",
                )
                if pushedLines == 1:
                    endColumn = ord("A") + len(data)
                    endColumn1 = ord("A") + (endColumn // ord("A")) - 1
                    endColumn2 = ord("A") + ((endColumn - ord("A")) % 26)
                    endColumn = chr(endColumn1) + chr(endColumn2)
                    # print("A2:" + endColumn + str(1 + len(data)))
                    dataSheet.format(
                        "A2:" + endColumn + str(1 + len(data)),
                        {
                            "backgroundColor": {
                                "red": color[0],
                                "green": color[1],
                                "blue": color[2],
                            }
                        },
                    )

                pushedLines += len(data)
                f = open(statsCsv, "w+")
                f.close()
            except Exception as e:
                print(e)

        live = True
        print("Finished authorizing, will update sheet every 30 seconds")
        while live:
            if pushedLines <= 1:
                push_data()
                if pushedLines > 1:
                    initialize_session()
            else:
                temp = pushedLines
                push_data()
                if pushedLines > temp:
                    # print("Updating session")
                    update_session()
            time.sleep(30)
    except Exception as e:
        print(e)
        input("")
