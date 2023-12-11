from flask import Flask, request
from typing import List, Union
import re

app = Flask(__name__)
response = ""
selected_items = []


class Menu:
    def __init__(self,
                 label: str,
                 title: str = "",
                 options: List["Menu"] = [],
                 default_options: Union["Menu", None] = None,
                 fallthrough: bool = False,
                 ) -> None:
        self.options = options
        self.label = label
        self.title = title
        self.default = default_options
        self.fallthrough = fallthrough
        self.ending = len(options) == 0 and default_options == None

    def get_item_string(self, text: str) -> str:
        if text == "":
            return self.to_string()

        path = text.split("*")
        try:
            if path[0] != "0":
                menu = self.get_option(int(path[0]))
            else:
                menu = self
        except:
            menu = self.get_option(None)

        return menu.get_item_string("*".join(path[1:]))

    def get_option(self, value: int | None) -> "Menu":
        if self.fallthrough or value == None:
            return self.default if self.default != None else self
        else:
            return self.options[value - 1] if self.options[value - 1] != None else self

    def to_string(self, ) -> str:
        string = f"CON {self.title}\n"
        for index, option in enumerate(self.options):
            string += f"{index+1}. {option.label}\n"

        string += f"{'0. Go back' if len(self.options) > 0 or self.ending else ''}"
        return string


items = [Menu(x) for x in ['Onions', 'Tomatoes', 'Rice', 'Beans', 'Fruits']]

item_flow = Menu(
    "", title="What do you sell", options=items,
    fallthrough=True,
    default_options=Menu("",
                         "What is the quantiy of items",
                         fallthrough=True,
                         default_options=Menu("",
                                              "What is the price of item",
                                              default_options=Menu(
                                                  "", title="You have successfuly added items to your items list",
                                              ),
                                              ),
                         )
)

menus = Menu("", "Welcome to Bodega", [
    Menu("To continue", "What service do you want to use", [
        Menu("Seller/Farmer", "What do you want to do", [
            Menu("Verify NIN", "Put your NIN number here",
                 default_options=Menu("", "Thank you for providing your NIN")),
            Menu("Manage Account", "", [
                Menu("See Orders", "Here a list of orders that you have"),
                Menu("Add Item",)
            ]),
            Menu("Sign Up", title="What is your full name",
                 default_options=Menu(label="", title="What is your location",  default_options=item_flow, fallthrough=True), fallthrough=True)
        ]),
        Menu("Buyer/Retailer", "What do you want to do", options=[
            Menu("See Orders", "Here's a list of orders that you have"),
            Menu("I want to buy something", "What do you want to buy",
                 [],
                 fallthrough=True,
                 default_options=Menu(
                     "",
                     "Here are some sellers we found",
                     items,
                     fallthrough=True,
                     default_options=Menu("",
                                          "We would send a message informing the seller about your request"),
                 ),
                 )
        ]),
        Menu("Loan", "What do type of loan do you want to apply for", [
            Menu("Farm loans")
        ]),
    ])
])


def main_menu():
    return "CON Welcome to Bodega\n1 To continue\n0 To leave"


def buy_sell_menu():
    return "CON Do you want to buy or sell?\n1 Sell\n2 Buy"


def items_menu():
    return "CON Items\n1 Onions\n2 Tomatoes\n3 Rice\n4 Beans\n5 Fruits"


def go_back(text):
    # Remove the last two parts of the text to go back dynamically
    parts = text.split("*")
    return "*".join(parts[:-1]) if len(parts) > 2 else ""


def select_item(item_number):
    item_dict = {
        '1': 'Onions',
        '2': 'Tomatoes',
        '3': 'Rice',
        '4': 'Beans',
        '5': 'Fruits'
    }
    item = item_dict.get(item_number)
    if item:
        selected_items.append(item)
        return f"CON You selected: {item}\n1 To finish\n0 To add an item"
    else:
        return "CON Invalid item number. Please try again."


@app.route('/test', methods=['POST', "GET"])
def test_ussd():
    global repsonse
    text = request.values.get("text")
    text = "" if text == None else text

    # The extra replace shit is for if we miss a last *0
    text = re.sub(r"\*\d+\*0", "", text).replace("*0", "")

    return menus.get_item_string(text)


@app.route('/', methods=['POST', 'GET'])
def ussd_callback():
    global response
    session_id = request.values.get("sessionId", None)
    service_code = request.values.get("serviceCode", None)
    phone_number = request.values.get("phoneNumber", None)
    text = request.values.get("text", "")
    text = re.sub(r"\*\d+\*0", "", text).replace("*0", "")

    # # Main Menu
    # if text == "":
    #     response = main_menu()

    # # Buy/Sell Menu
    # elif text == "1":
    #     response = buy_sell_menu()

    # # Items Menu
    # elif text == "1*1" or text == "1*2":
    #     # THis was before
    #     # response = "items_menu"
    #     response = items_menu()

    # # Item Select Menu
    # elif text.startswith("1*1*") and text.split("*")[-1] in ["1", "2", "3", "4", "5"]:
    #     item_num = text.split('*')[-1]
    #     response = select_item(item_num)

    # # Final Menu
    # elif len(text) == 7 and text[-1] == "1":
    #     items = " ".join(selected_items)
    #     response = f"END You are {response}. Your items include {items}.\nYou'll be sent a list of contacts"
    # # To go back to previous menu
    # elif text[len(text)-1] == "0":
    #     text = go_back(text)
    #     return response
    return menus.get_item_string(text)


if __name__ == "__main__":
    app.run(debug=True)
