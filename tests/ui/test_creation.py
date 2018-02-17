from power_hour_creator.ui.creation import PowerHourOutputLocator

def test_power_hour_output_locator_should_have_default_dir_on_all_platforms():
    locator = PowerHourOutputLocator(
        export_is_video=True,
        parent=None,
        settings=None
    )

    locator.default_vid_dir['darwin']
    locator.default_vid_dir['windows']
    locator.default_vid_dir['linux']
