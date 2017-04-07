# Created by jac24 at 2/8/2017
Feature: Create power hour

  Scenario: Creating an audio power hour with default and custom start times, and a full song
    When I add 2 tracks to a power hour
    And I add a full song to the power hour
    And I set track 1's start time to 0:00
    And I create a power hour
    Then that power hour should have been created

  Scenario: I should be able to move around the tracklist and create a power hour without errors
    When I add 1 tracks to a power hour
    And I click around the tracklist start times
    And I create a power hour
    Then that power hour should have been created

  Scenario: I should not be able to create a power hour if I haven't entered a url
    When I forget to add a track to the power hour
    Then I should not be able to create a power hour

  Scenario: I should be able to create a video power hour with all the features
    When I add 2 videos to a video power hour with one full song
    And I set track 1's start time to 0:00
    And I create a video power hour
    Then that video power hour should have been created