# Created by jac24 at 2/8/2017
Feature: Create power hour

  Scenario: Creating a power hour with default and custom start times
    When I add 2 tracks to a power hour
    And I set track 1's start time to 0:00
    And I create a power hour
    Then that power hour should have been created

  Scenario: I should be able to move around the tracklist and create a power hour without errors
    When I add 1 tracks to a power hour
    And I click around the tracklist start times
    And I create a power hour
    Then that power hour should have been created
