from PyQt5.QtTest import QTest


def test_users_should_be_able_to_delete_power_hour_from_list(
        main_window_component,
        phs_list_component):
    main_window_component.add_power_hour()
    phs_list_component.delete_power_hour(index=1)

    assert phs_list_component.num_power_hours == 1
    assert phs_list_component.power_hour_is_selected


def test_users_should_see_no_track_after_deleting_only_power_hour(
        phs_list_component,
        tracklist_component):
    phs_list_component.delete_power_hour(index=0)
    assert 0 == tracklist_component.row_count


def test_users_should_see_no_context_menu_if_no_power_hours_in_list(
        phs_list_component):
    pos = phs_list_component.row_pos(0)
    phs_list_component.delete_power_hour(index=0)
    menu = phs_list_component.open_context_menu_at(pos)
    assert 0 == len(menu.actions())
