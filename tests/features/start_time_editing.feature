# Created by Jimmy at 2/11/2017
Feature: Start time editing
  # Enter feature description here

  Scenario: Default start time should be in time format
    When I add 1 tracks to a power hour
    Then I should see the start time in the correct format