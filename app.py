import re
from flask import Flask, request
from typing import List, Union

app = Flask(__name__)


class Menu:
    def __init__(self,
                 label: str,
                 title: str = "",
                 options: List["Menu"] = [],
                 default_options: Union["Menu", None] = None,
                 fallthrough: bool = False,
                 ending: bool = False,
                 show_back: bool = False,
                 ) -> None:
        self.parent: Union[Menu, None] = None
        self.options = options
        for option in self.options:
            option.parent = self
        self.label = label
        self.title = title
        self.default = default_options
        if self.default != None:
            self.default.parent = self
        self.fallthrough = fallthrough
        self.ending = ending
        self.show_back = show_back

    def get_item_string(self, text: str) -> str:
        if text == "":
            return self.to_string()

        path = text.split("*")
        try:
            if path[0] != "0":
                menu = self.get_option(int(path[0]))
            else:
                menu = self.parent if self.parent != None else self
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

        string += f"{'0. Go Back' if len(self.options) > 0 or self.show_back else ''}"
        return string


def get_items() -> List[Menu]:
    return [Menu(x) for x in ['Yam', 'Tomatoes', 'Rice', 'Beans', 'Fruits']]


def get_order_menu() -> Menu:
    return Menu("Olalekan Adeoye - 100 Yams @₦220,000",
                "What do you want to do with the order 'Olalekan Adeoye - 100 Yams@ ₦220,000'", [
                    Menu("Accept",
                         "We inform the buyer of the interest to sell. Expect a SMS with more information",
                         ending=True),
                    Menu("Reject",
                         "We inform the buyer that you are not willing to sell.",
                         ending=True)
                ])


def get_main_menu(phone_number: str = ""):
    return Menu("", "Welcome to Bodega", [
        Menu("To continue", "What service do you want to use", [
            Menu("Set up your account with us", "Enter your NIN Number",
                default_options=Menu(
                    "",
                    "Enter your Federal Ministry of Agriculture and Food Security Licence Number",
                    default_options=Menu("", "Thank you for signing up for the platform", ending=True, ),),
                 ),
            Menu("Get access to the market", "", options=[
                Menu("Manage Products", "Manage your product", options=[
                    Menu(
                        "Product List", "Here are the products that you listed on the market", [
                            Menu("Yam")
                        ]),
                    Menu("Add Product", "What product do you want to add",
                         options=get_items(), fallthrough=True, default_options=Menu("", "You added the product to your product list", show_back=True),),
                    Menu("Remove Product", "What product do you want to remove",
                         options=[get_items()[0]], fallthrough=True, default_options=Menu("", "You removed the product to your product list", show_back=True),),
                ]),
                Menu("See Orders", "Here a list of orders that you have", options=[
                    get_order_menu()
                ]),
            ]),
            Menu("Get start up funding and helps", "Who do you want to get support from", [
                Menu("Government", "Here are the organizations under the government that have plans", options=[
                    Menu("Federal Ministry of Agriculture and Food Security", "Here are the plans", [
                        Menu("Loan of ₦500,000 for 6 months",),
                        Menu("Loan of ₦1,000,000 for 12 months",),
                        Menu("Loan of ₦1,500,000 for 18 months",),
                    ], fallthrough=True, default_options=Menu("", "We are processing your request. You will recieve a SMS on the progress application", ending=True),),
                ]),
                Menu("Angel Investors",
                     "Sorry there are no offers right now, We'll inform you of when an offer opens", show_back=True),
                Menu(
                    "NGOs", "Sorry there are no offers right now, We'll inform you of when an offer opens", show_back=True),
            ]),
        ])])


@app.route('/test', methods=['POST', "GET"])
def test_ussd():
    global repsonse
    text = request.values.get("text", "")

    return get_main_menu().get_item_string(text)


@app.route('/', methods=['POST', 'GET'])
def ussd_callback():
    global response
    session_id = request.values.get("sessionId", None)
    service_code = request.values.get("serviceCode", None)
    phone_number = request.values.get("phoneNumber", "")
    text = request.values.get("text", "")

    return get_main_menu().get_item_string(text)


if __name__ == "__main__":
    app.run(debug=True)
