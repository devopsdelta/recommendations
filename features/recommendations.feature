Feature: The recommendations api service back-end
    As a E-commerce Store Owner
    I need a RESTful recommendations service
    So that I can inform customers who are purchasing a product of similar or related products that may also want to purchase

Background:
    Given the following recommendations
    #     | Detail_ID | Product_ID | Type_ID | Recommendation_Prod_ID | Weight |
    #     | 1         | 123        | 1       | 32                     | .6     |
    #     | 2         | 123        | 1       | 34                     | .6     |
    #     | 3         | 123        | 1       | 45                     | .6     |
    #     | 4         | 123        | 2       | 23                     | .6     |
    #     | 5         | 123        | 2       | 33                     | .6     |
    #     | 6         | 123        | 3       | 43                     | .6     |
    # When I visit the "Home Page"
    # Then I should see "Recommendation Demo REST API Service" in the title
    # And I should not see "404 Not Found"

# Scenario: Create a Recommendation
#     When I visit the "Home Page"
#     And I set the "Product_ID" to "123"
#     And I set the "Type" to "up-sell"
#     And I press the "Create" button
#     Then I should see the message "Success"
#
# Scenario: List all pets
#     When I visit the "Home Page"
#     And I press the "Search" button
#     Then I should see "fido" in the results
#     And I should see "kitty" in the results
#     And I should see "leo" in the results
#
# Scenario: List all dogs
#     When I visit the "Home Page"
#     And I set the "Category" to "dog"
#     And I press the "Search" button
#     Then I should see "fido" in the results
#     And I should not see "kitty" in the results
#     And I should not see "leo" in the results
#
# #tbd
# Scenario: Update a Pet
#     When I visit the "Home Page"
#     And I set the "Id" to "1"
#     And I press the "Retrieve" button
#     Then I should see "fido" in the "Name" field
#     When I change "Name" to "Boxer"
#     And I press the "Update" button
#     Then I should see the message "Success"
#     When I set the "Id" to "1"
#     And I press the "Retrieve" button
#     Then I should see "Boxer" in the "Name" field
#     When I press the "Clear" button
#     And I press the "Search" button
#     Then I should see "Boxer" in the results
#     Then I should not see "fido" in the results
