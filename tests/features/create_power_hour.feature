# Created by jac24 at 2/8/2017
Feature: Create power hour

  Scenario: Creating a power hour with default start times
    When I add a track to a power hour
    And I create a power hour
    Then that power hour should have been created