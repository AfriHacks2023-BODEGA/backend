from flask import Flask, request
from typing import List, Union
import re

app = Flask(__name__)
response = ""
selected_items = []

# menus = Menu("", "Welcome to Bodega", [
#     Menu("To continue", "What service do you want to use", [
#         Menu("Seller/Farmer", "What do you want to do", [
#             Menu("Verify NIN", "Put your NIN number here",
#                  default_options=Menu("", "Thank you for providing your NIN", ending=True)),
#             Menu("Manage Account", "", [
#                 Menu("See Orders", "Here a list of orders that you have",
#                      options=[order],),
#                 Menu("Add Item", default_options=item_flow)
#             ]),
#             Menu("Sign Up", title="What is your full name",
#                  default_options=Menu(label="", title="What is your location",  default_options=item_flow, fallthrough=True), fallthrough=True)
#         ]),
#         Menu("Buyer/Retailer", "What do you want to do", options=[
#             Menu("See Orders", "Here's a list of orders that you have"),
#             Menu("I want to buy something", "What do you want to buy",
#                  items,
#                  fallthrough=True,
#                  default_options=Menu(
#                      "",
#                      "Here are some sellers we found",
#                      [placing_order],
#                      fallthrough=True,
#                      default_options=Menu("",
#                                           "We would send a message informing the seller about your request", ending=True),
#                  ),
#                  )
#         ]),
#         Menu("Loan", "What do type of loan do you want to apply for", [
#             Menu("Farm loans")
#         ]),
#     ])
# ])


class Menu:
    def __init__(self,
                 label: str,
                 title: str = "",
                 options: List["Menu"] = [],
                 default_options: Union["Menu", None] = None,
                 fallthrough: bool = False,
                 ending: bool = False
                 ) -> None:
        self.options = options
        self.label = label
        self.title = title
        self.default = default_options
        self.fallthrough = fallthrough
        self.ending = ending

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
        string = f"{'END' if self.ending else 'CON'} {self.title}\n"

        for index, option in enumerate(self.options):
            string += f"{index+1}. {option.label}\n"

        string += f"{'0. Go back' if len(self.options) > 0 else ''}"
        return string


items = [Menu(x) for x in ['Yam', 'Tomatoes', 'Rice', 'Beans', 'Fruits']]

order = Menu("Olalekan Adeoye - 100 Yams @₦220,000",
             "What do you want to do with the order 'Olalekan Adeoye - 100 Yams@ ₦220,000'", [
                 Menu("Accept",
                      "We inform the buyer of the interest to sell. Expect a SMS with more information",
                      ending=True),
                 Menu("Reject",
                      "We inform the buyer that you are not willing to sell.",
                      ending=True)
             ])
placing_order = Menu("Olalekan Adeoye - 12 Yam@₦10,000")


def get_main_menu():
    return Menu("", "Welcome to Bodega", [
        Menu("To continue", "What service do you want to use", [
            Menu("Set up your account with us", "Enter your NIN Number",
                default_options=Menu(
                    "",
                    "Enter your Federal Ministry of Agriculture and Food Security Licence Number",
                    default_options=Menu("", "Thank you for signing up for the platform", ending=True),),
                 ),
            Menu("Get access to the market", "", options=[
                Menu("Manage Products", "Manage your product", options=[
                    Menu(
                        "Product List", "Here are the products that you listed on the market", [
                            Menu("Yam")
                        ]),
                    Menu("Add Product", "What product do you want to add",
                         options=items, fallthrough=True, default_options=Menu("", "You added the product to your product list", ending=True),),
                    Menu("Remove Product", "What product do you want to remove",
                         options=[items[0]], fallthrough=True, default_options=Menu("", "You removed the product to your product list", ending=True),),
                ]),
                Menu("See Orders", "Here a list of orders that you have", options=[
                    order
                ]),
            ]),
            Menu("Get start up funding and helps", "Choose provider", [
                Menu("Government", "Here are the organizations under the government that have plans", options=[
                    Menu("Federal Ministry of Agriculture and Food Security", "Here are the plans", [
                        Menu("Loan of ₦500,000 for 6 months",),
                        Menu("Loan of ₦1,000,000 for 12 months",),
                        Menu("Loan of ₦1,500,000 for 18 months",),
                    ], fallthrough=True, default_options=Menu("", "We are processing your request. You will recieve a SMS on the progress application", ending=True),),
                ]),
                Menu("Angel Investors",
                     "Sorry there are no offers right now, We'll inform you of when an offer opens", ending=True),
                Menu(
                    "NGOs", "Sorry there are no offers right now, We'll inform you of when an offer opens", ending=True),
            ]),
        ])])


@app.route('/test', methods=['POST', "GET"])
def test_ussd():
    global repsonse
    text = request.values.get("text")
    text = "" if text == None else text

    # The extra replace shit is for if we miss a last *0
    text = re.sub(r"\*\d+\*0", "", text).replace("*0", "")

    return get_main_menu().get_item_string(text)


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
    return get_main_menu().get_item_string(text)


if __name__ == "__main__":
    app.run(debug=True)
