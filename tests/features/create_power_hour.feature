# Created by jac24 at 2/8/2017
Feature: Create power hour

  Scenario: Creating an audio power hour with default and custom start times, and a full song
    When I add 2 tracks to a power hour
    And I add a full song to the power hour
    And I set track 1's start time to 0:00
    And I set track 2's start time to 0:00.45
    And I create a power hour
    Then that power hour should have been created
    And I should see the power hour created message

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

  Scenario: I should be able to add a track above with the right click menu
    When I add a track to the power hour at row 1
    And I choose to insert a row above row 1 with the context menu
    And I add a track to the power hour at row 1
    Then the row count should have increased
    And the second track should be above the first

  Scenario: I should be able to add a track below with the right click menu
    When I add a track to the power hour at row 1
    And I add a track to the power hour at row 2
    And I choose to insert a row below row 1 with the context menu
    And I add a track to the power hour at row 2
    Then the row count should have increased
    And there should be 3 tracks in the power hour

  Scenario: I should be able to delete rows from the context menu
    When I add 3 tracks to a power hour
    And I choose to delete the tracks at row 2
    Then there should be 2 tracks in the power hour

  Scenario: Creating a new power hour from the file menu
    When I create a new power hour from the file menu
    And I change that power hour's name
    Then I should see the new power hour name above the tracklist

  Scenario: Persisting a power hour so that it is still there on the next load
    When I create a new power hour from the file menu
    And I add 2 tracks to a power hour
    And I reload the app
    And I select the power hour I created
    Then I should still see the tracks I added

  Scenario: Adding a track with the context menu when there are no other tracks
    When I remove all the tracks from a power hour
    And I add a new track to the power hour with the context menu
    Then there should be a track in the power hour

  Scenario: I should see a message in the status bar if there's an error downloading a track's info
    When there's an error downloading track info
    Then I should see a message in the status bar

  Scenario: I should be able to cancel creating a power hour
    When I add 2 tracks to a power hour
    And I add a full song to the power hour
    And I create a power hour
    And I click cancel
    Then I should see that the export is cancelling
    And that power hour should have been cancelled
    And I should not see the power hour created message

  Scenario: I should be able to view a local track's info
    When I add a local video to a power hour
    Then I should see that track's info

  Scenario: I should be able to create a video power hour with a local video
    When I add a local video to a power hour
    And I set track 1's start time to 0:00
    And I add 1 tracks to a power hour
    And I create a video power hour
    Then that video power hour should have been created

