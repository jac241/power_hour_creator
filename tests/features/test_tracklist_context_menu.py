def test_users_should_see_no_context_menu_if_they_delete_all_of_their_power_hours(
        phs_list_component,
        tracklist_component):
    pos = tracklist_component.row_pos(1)
    phs_list_component.delete_power_hour(index=0)
    menu = tracklist_component.open_context_menu_at(pos)
    assert len(menu.actions()) == 0


def test_users_should_not_see_track_dependent_context_menu_items_if_no_track_highlighted(
        tracklist_component):
    pos = tracklist_component.row_pos(59)
    tracklist_component.delete_track(59)
    menu = tracklist_component.open_context_menu_at(pos)
    assert len(menu.actions()) == 1
