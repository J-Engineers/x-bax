USER_TYPES = [
    "customer",
    "purchaser",
    "delivery",
    "ict",
    "area representative",
    "area accountant",
    "state admin",
    "state representative",
    "state accountant",
    "admin 1",
    "admin 2",
    "accountant general",
    "owner"
]
USER_TYPES_DETAILS = "User types are from level 0 to  level 12. Where level 0 is customer, level 1 is purchase, " \
                     "level 2 is the delivery, level 3 is the ict, level 4 is the area representative, level 5 is " \
                     "the area accountant, " \
                     "level 6 is the state admin, level 7 is the state representative, level 8 is the state " \
                     "accountant, level 9 is the admin 1, " \
                     "level 10 is the admin 2, level 11 is the  accountant general, level 12 is the CEO"
USER_ROLE = {
    "role_0": [
        {
            'name': 'Customer',
            'duty': 'You would have a list of the major markets in your country, you can visit any market of your '
                    'choice without going there physically, just tell us what you are looking for in the any of the '
                    'markets and we will tell you the current price, buy for you and bring it to any location of your'
                    ' choice. However if you do not know which market to find what you want to buy, you can simply tell'
                    ' us only what you want to buy, we would search all the markets for it and bring you the different '
                    'markets that has the goods and their prices. No stree, no hassle ... wellcome to an easy life',
            'code': 0,
            'target': 'customer'
        }
    ],
    "role_1": [
        {
            'name': 'Purchaser',
            'duty': 'You would have a list of orders  from customers in your market as assigned to you. '
                    'You would be in position of company master card and enter the market to buy the goods and as well '
                    'pay for the goods, bring the goods and the receipt to the office which our office would be in the '
                    ' market. You would be paid by commission, No stree, no hassle ... wellcome to an easy life',
            'code': 1,
            'target': 'purchaser'
        }
    ],
    "role_2": [
        {
            'name': 'Delivery',
            'duty': 'You would have a list of orders from us to deliver from our office to the address'
                    'we will give you, you will be paid by commission',
            'code': 2,
            'target': 'delivery'
        }
    ],
    "role_3": [
        {
            'name': 'Ict',
            'duty': 'You would have a list of orders from customers, you will verify the price in the market and '
                    'update the app  with current price, where you do not have the goods in the market you were '
                    'assigned to, you will report to the area representative, where you saw the goods, you will update'
                    'the price in the app. You will assign a purchaser to orders, when goods has '
                    'been purchased and brought to the office at the market which is your workplace. '
                    'you will assign delivery to the order, when the delivery is back, you will call the customer'
                    'to confirm they received their package, you will be paid  monthly',
            'code': 3,
            'target': 'ict'
        }
    ],
    "role_4": [
        {
            'name': 'Area Representative',
            'duty': 'You will monitor the purchaser, the delivery, the ict and the accountant. Where they need help'
                    'you will have to be the first person they would reach out to, where you cannot solve their'
                    'problem, you would report to the state representative. You will recruit your staff including'
                    'purchaser, the delivery and you will survey good markets to feature and you will register the'
                    'markets.',
            'code': 4,
            'target': 'area_representative'
        }
    ],
    "role_5": [
        {
            'name': 'Area Accountant',
            'duty': 'You will monitor the purchaser, the delivery, the ict'
                    'Where they need help, you will have to be the first person they would reach out to,'
                    ' where you cannot solve their problem, you would report to the area representative. '
                    'You will approve all money transfer by customers into their wallets'
                    'you will approve all money transfer from their wallet back to their account'
                    'you will approve all the money transfer from their wallet to our account',
            'code': 5,
            'target': 'area_accountant'
        }
    ],
    "role_6": [
        {
            'name': 'State Admin',
            'duty': 'You will monitor the area accountant operations and area representative operations'
                    'You will recruit the  area representative'
                    'You will update a market list when it comes  to the state level and yet goods not found'
                    'You will make a call or chat to verify if the customer want us to further look for the goods  '
                    'in other states. if yes you will update the list to be available for other states',
            'code': 6,
            'target': 'state_admin'
        }
    ],
    "role_7": [
        {
            'name': 'State Representative',
            'duty': 'You will monitor the state admin operations and state  accountant operation'
                    'You are in charge of this platform for the state'
                    'You are in charge of settling disputes in your state and you are in charge of refunds'
                    'You are one of the management committee',
            'code': 7,
            'target': 'state_representative'
        }
    ],
    "role_8": [
        {
            'name': 'State Accountant',
            'duty': 'You will monitor the state admin operations'
                    'You are in charge of this platform finance for the state'
                    'You are in charge of refunds account balancing'
                    'You are one of the management committee',
            'code': 8,
            'target': 'state_accountant'
        }
    ],
    "role_9": [
        {
            'name': 'Admin 1',
            'duty': 'You will enforce the ict and the purchaser in the markets  and state admin to do their work as '
                    'fast as possible You will report any bad conduct to the area representative'
                    'Any suspension, you would report to the state representative'
                    'You are one of the management committee',
            'code': 9,
            'target': 'admin_1'
        }
    ],
    "role_10": [
        {
            'name': 'Admin 2',
            'duty': 'You will enforce the area accountant and state accountant to their work'
                    'You will report any bad conduct to the owner'
                    'Any suspension, you would report to the owner'
                    'You are one of the management committee',
            'code': 10,
            'target': 'admin_2'
        }
    ],
    "role_11": [
        {
            'name': 'General Accountant',
            'duty': 'You will monitor the area accountant and state accountant operations'
                    'You will report any bad conduct to the owner'
                    'Any suspension, you would report to the owner',
            'code': 11,
            'target': 'general_accountant'
        }
    ],
    "role_12": [
        {
            'name': 'Owner',
            'duty': 'Maintain peace in the system',
            'code': 12,
            'target': 'owner'
        }
    ]
}
