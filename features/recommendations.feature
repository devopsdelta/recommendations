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
    When I visit the "Recommendation Details" page
    And I press the "Search" button
    Then I should see "29" in the search_results
    And I should see "23" in the search_results
    And I should see "567" in the search_results
    And I should not see "100" in the search_results

Scenario: List all up-sell recommendations
    When I visit the "Recommendation Details" page
    And I set the "rec_type_name" to "up-sell"
    And I press the "Search" button
    Then I should see "567" in the search_results
    And I should not see "29" in the search_results
    And I should not see "23" in the search_results

Scenario: Create a Recommendation
    When I visit the "Recommendation Details" page
    And I enter the "Product" to "84"
    And I enter the "Rec_Product" to "621"
    And I enter the "Rec_Type" to "Accessory"
    And I enter the "Weight" to "0.8"
    And I press the "Save" button
    Then I should see the message "Created"

Scenario: Update a Recommendation
    When I visit the "Recommendation Details" page
    And I press the "Search" button
    And I press the "edit_1" button
    Then I should see "1" in the "rec_id" field
    And I should see "29" in the "product_id" field
    And I should see "2" in the "rec_type_id" field
    And I should see "51" in the "rec_product_id" field
    And I should see "0.2" in the "weight_id" field
    And I set the "product_id" to "8755"
    And I press the "Save" button
    And I should see the message "Updated"
    And I should see "8755" in the "product_id" field
