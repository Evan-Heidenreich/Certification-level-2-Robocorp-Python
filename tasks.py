from robocorp.tasks import task
from robocorp import browser
from RPA.HTTP import HTTP
from RPA.Tables import Tables
from RPA.PDF import PDF
from RPA.Archive import Archive

@task
def order_robots_from_RobotSpareBin():
    """
    Orders a robot from RobotSpareBin Industries Inc
    Saves the order HTML receipt as a PDF file
    Saves the screenshot of the ordered robot
    Embeds the screenshot of the robot to the PDF receipt
    Creates a ZIP archive of the receipts and images
    """
    browser.configure(slowmo=100)
    open_robot_order_website()

    close_annoying_modal()

    download_csv_file()

    orders = get_orders()
    for order in orders:
        order_num = order["Order number"]
        Head = order["Head"]
        Body = order["Body"]
        Legs = order["Legs"]
        Address = order["Address"]

    fill_form_with_csv_data(orders)

    archive_receipts()

def open_robot_order_website():
    """Opens the Robot Order Website"""
    browser.goto("https://robotsparebinindustries.com/#/robot-order")

def close_annoying_modal():
    """This Function closes the pop up when the website is opened"""
    page = browser.page()
    page.click("text=OK")

def download_csv_file():
    """Download the csv file and read the file into a table"""
    http = HTTP()
    http.download(url="https://robotsparebinindustries.com/orders.csv", overwrite=True)

def fill_and_submit_robot_order_form(row):
    """Fill and submit the robor order form"""
    page = browser.page()
     
    page.select_option("#head", row['Head'])
    page.check(f"#id-body-" + row['Body'])
    page.fill(".form-control", row["Legs"])
    page.fill("#address", str(row["Address"]))
    page.click("#preview")
    page.click("#order")

    while not page.query_selector("#order-another"):
        page.click("#order")
    pdf_file = store_receipt_as_pdf(row["Order number"])
    
    screenshot = screenshot_robot(row["Order number"])

    embed_screenshot_to_receipt(screenshot, pdf_file)

    page.click("#order-another")
    close_annoying_modal()

def fill_form_with_csv_data(orders):
    """For loop that calls our fill and submit function"""
    for row in orders:
        fill_and_submit_robot_order_form(row)

def get_orders():
    """This function gets the order data and fills the robot order form"""
    tables = Tables()
    orders = tables.read_table_from_csv("orders.csv", header=True)
    return orders

def store_receipt_as_pdf(order_num):
    """save the receipt as a PDF"""
    page = browser.page()

    receipt_html = page.locator("#receipt").inner_html()
    pdf = PDF()
    pdf_file = f"output/{order_num}.pdf"
    pdf.html_to_pdf(receipt_html, pdf_file)
    return pdf_file

def screenshot_robot(order_num):
    """Takes a screenshot of the robot"""
    page = browser.page()
    screenshot = f"output/{order_num}.png"
    page.screenshot(path=screenshot)    
    return screenshot

def embed_screenshot_to_receipt(screenshot, pdf_file):
    """Embed the screenshot to the receiot pdf"""
    pdf = PDF()
    pdf.add_files_to_pdf(files=[screenshot], target_document = pdf_file, append=True)

def archive_receipts():
    lib = Archive()
    lib.archive_folder_with_zip('output', 'output/orders.zip', include='*.pdf')
