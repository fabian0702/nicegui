from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

from nicegui import ui

from .screen import Screen


def test_entering_color(screen: Screen):
    ui.color_input(label='Color', on_change=lambda e: ui.label(f'content: {e.value}'))

    screen.open('/')
    screen.type(Keys.TAB)
    screen.type('#001100')
    screen.should_contain('content: #001100')


def test_picking_color(screen: Screen):
    ui.color_input(label='Color', on_change=lambda e: output.set_text(e.value))
    output = ui.label()

    screen.open('/')
    screen.click('colorize')
    screen.click_at_position(screen.find('HEX'), x=0, y=60)
    content = screen.selenium.find_element(By.CLASS_NAME, 'q-color-picker__header-content')
    assert content.value_of_css_property('background-color') in {'rgba(245, 186, 186, 1)', 'rgba(245, 184, 184, 1)'}
    assert output.text in {'#f5baba', '#f5b8b8'}

    screen.type(Keys.ESCAPE)
    screen.wait(0.5)
    screen.should_not_contain('HEX')

    screen.click('colorize')
    content = screen.selenium.find_element(By.CLASS_NAME, 'q-color-picker__header-content')
    assert content.value_of_css_property('background-color') in {'rgba(245, 186, 186, 1)', 'rgba(245, 184, 184, 1)'}
    assert output.text in {'#f5baba', '#f5b8b8'}
