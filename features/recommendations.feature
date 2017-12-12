Feature: The recommendations api service back-end
    As a E-commerce Store Owner
    I need a RESTful recommendations service
    So that I can inform customers who are purchasing a product of similar or related products that may also want to purchase

Background:
    Given the following recommendations
        | rec_id | product_id | rec_type_id | rec_product_id | weight |
        | 1      | 29         | 2           | 51             | 0.2    |
        | 2      | 567        | 1           | 449            | .6     |
        | 3      | 23         | 3           | 33             | .6     |
        
Scenario: My server is running
     When I visit the "Home Page"
     Then I should see "Recommendation" in the title
     And I should not see "404 Not Found"

Scenario: Get a recommendation
    When I visit the "Recommendation Details" page for recommendation detail "1"
    Then I will see a "rec_id" with "1" in my results
    And I will see a "product_id" with "29" in my results
    And I will see a "rec_type_id" with "2" in my results
    And I will see a "rec_product_id" with "51" in my results
    And I will see a "weight" with "0.2" in my results
    And I should not see "rof-riders" in my results

Scenario: List all recommendations
    When I visit the "Recommendation Details" page of all recommendations
    Then I should see "29" in the results
    And I should see "23" in the results
    And I should see "567" in the results
    And I should not see "100" in the results

Scenario: List all up-sell recommendations
    When I visit the Recommendation Details page of filter recommendations by type "up-sell"
    And I set the "Type" to "up-sell"
    And I press the "Search" button
    Then I should see "567" in the search_results
    And I should not see "29" in the search_results
    And I should not see "23" in the search_results

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
