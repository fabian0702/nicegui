from selenium.webdriver import Keys

from nicegui import ui

from .screen import Screen


def test_select(screen: Screen):
    ui.select(['A', 'B', 'C'], value='A')

    screen.open('/')
    screen.should_contain('A')
    screen.should_not_contain('B')
    screen.should_not_contain('C')

    screen.click('A')  # open the dropdown
    screen.click('B')  # close the dropdown
    screen.wait(0.5)
    screen.should_not_contain('A')
    screen.should_contain('B')
    screen.should_not_contain('C')


def test_select_with_input(screen: Screen):
    ui.select(['A', 'AB', 'XYZ'], with_input=True)

    screen.open('/')
    screen.find_by_tag('input').click()
    screen.should_contain('XYZ')

    screen.find_by_tag('input').send_keys('A')
    screen.wait(0.5)
    screen.should_contain('A')
    screen.should_contain('AB')
    screen.should_not_contain('XYZ')

    screen.find_by_tag('input').send_keys('ABC' + Keys.ENTER)
    screen.find_by_tag('input').click()
    screen.should_not_contain('ABC')


def test_replace_select(screen: Screen):
    with ui.row() as container:
        ui.select(['A'], value='A')

    def replace():
        container.clear()
        with container:
            ui.select(['B'], value='B')
    ui.button('Replace', on_click=replace)

    screen.open('/')
    screen.should_contain('A')
    screen.click('Replace')
    screen.should_contain('B')
    screen.should_not_contain('A')


def test_multi_select(screen: Screen):
    s = ui.select(['Alice', 'Bob', 'Carol'], value='Alice', multiple=True).props('use-chips')
    ui.label().bind_text_from(s, 'value', backward=str)

    screen.open('/')
    screen.should_contain("['Alice']")
    screen.click('Alice')
    screen.click('Bob')
    screen.should_contain("['Alice', 'Bob']")

    screen.click('cancel')  # remove icon
    screen.should_contain("['Bob']")


def test_changing_options(screen: Screen):
    s = ui.select([10, 20, 30], value=10)
    ui.label().bind_text_from(s, 'value', lambda v: f'value = {v}')
    ui.button('reverse', on_click=lambda: (s.options.reverse(), s.update()))
    ui.button('clear', on_click=lambda: (s.options.clear(), s.update()))

    screen.open('/')
    screen.click('reverse')
    screen.should_contain('value = 10')
    screen.click('clear')
    screen.should_contain('value = None')


def test_set_options(screen:  Screen):
    s = ui.select([1, 2, 3], value=1)
    ui.button('Set new options', on_click=lambda: s.set_options([4, 5, 6], value=4))

    screen.open('/')
    screen.click('Set new options')
    screen.click('4')
    screen.should_contain('5')
    screen.should_contain('6')


def test_add_new_values(screen:  Screen):
    ui.select(options=['1', '2', '3'], new_value_mode='add-unique')

    screen.open('/')
    screen.find_by_tag('input').send_keys('123' + Keys.TAB)
    screen.wait(0.5)
    screen.find_by_tag('input').click()
    screen.should_contain('123')


def test_add_new_values_with_options_dict(screen:  Screen):
    ui.select(options={1: '1', 2: '2', 3: '3'}, new_value_mode='add-unique')

    screen.open('/')
    screen.find_by_tag('input').send_keys('123' + Keys.TAB)
    screen.wait(0.5)
    screen.find_by_tag('input').click()
    screen.should_contain('123')


def test_add_new_values_with_multiple(screen:  Screen):
    s = ui.select(options=['1', '2', '3'], value='1', multiple=True, new_value_mode='add-unique').props('use-chips')
    ui.label().bind_text_from(s, 'value', backward=str)

    screen.open('/')
    screen.should_contain("['1']")
    screen.find_by_tag('input').send_keys('123' + Keys.ENTER)
    screen.wait(0.5)
    screen.find_by_tag('input').click()
    screen.should_contain('123')
    screen.click('123')
    screen.should_contain("['1', '123']")
