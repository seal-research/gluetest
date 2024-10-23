from selenium import webdriver
from selenium.webdriver.common.by import By
import time

if __name__ == "__main__":
    driver = webdriver.Edge()

    #change commons-cli to commons-csv or other to get project based on different dependents
    driver.get("https://github.com/apache/commons-cli/network/dependents")

    for i in range(1600):

        while True:
            try:
                time.sleep(2)  
                
                box = driver.find_elements(by=By.CLASS_NAME, value="Box")
                # print(box)
                rows = box[0].find_elements(by=By.CLASS_NAME, value="Box-row.d-flex.flex-items-center")
                hrefs = []
                for row in rows:
                    line = ""
                    samples = row.find_elements(by=By.TAG_NAME, value="a")
                    for sample in samples:
                        if sample.get_attribute("data-hovercard-type")=="repository":
                            line = line + sample.get_attribute("href") + ","
                    numbers = row.find_elements(by=By.TAG_NAME, value="span")
                    for number in numbers:
                        if number.get_attribute("class")=="color-fg-muted text-bold pl-3":
                            line = line + number.text + ","
                    print(line[:-1])

                pagi_container = driver.find_elements(by=By.CLASS_NAME, value="paginate-container")
                # print(pagi_container)
                buttons = pagi_container[0].find_elements(by=By.TAG_NAME, value="a")
                for button in buttons:
                    if button.text == "Next":
                        button.click()
            except Exception:
                time.sleep(5)
                continue
            else:
                break
            
    driver.quit()
