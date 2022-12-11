from models import Counter, CounterInfo
from typing import List

BTN_BG_COLOR = '#ffdbac'
BTN_FONT_COLOR = '#000000'
BTN_MENU_BG_COLOR = "#ababab" 

BTN_WIDTH_IN_COLUMNS = 2
BTN_HEIGHT_IN_ROWS = 2

AB_ADD_POWER_METER_CMD = "add_power_meter_cmd"
AB_ADD_POWER_METER_VALUE_CMD = "add_power_meter_value_cmd"
AB_ADD_POWER_METER_BY_CONTRACT_CMD = "add_power_meter_by_contract_cmd"
AB_DELETE_POWER_METER_CMD = "delete_power_meter_cmd"
AB_HELP_CMD = "help_cmd"
AB_MAIN_MENU_CMD = "main_menu_cmd"
AB_START_CMD = "start_cmd"


main_menu_keyboard = {
	"Type": "keyboard",
	"Buttons": [
		{
			"Columns": BTN_WIDTH_IN_COLUMNS,
			"Rows": BTN_HEIGHT_IN_ROWS,
			"Text": "<font color='{0}'>Додати показник лічильника</font><br><br>".format(BTN_FONT_COLOR),
			"TextSize": "medium",
			"TextHAlign": "center",
			"TextVAlign": "center",
			"ActionType": "reply",
			"ActionBody": AB_ADD_POWER_METER_VALUE_CMD,
			"BgColor": BTN_BG_COLOR,
			"Image": ""
		},
		{
			"Columns": BTN_WIDTH_IN_COLUMNS,
			"Rows": BTN_HEIGHT_IN_ROWS,
			"Text": "<font color='{0}'>Додати лічильник</font><br><br>".format(BTN_FONT_COLOR),
			"TextSize": "medium",
			"TextHAlign": "center",
			"TextVAlign": "center",
			"ActionType": "reply",
			"ActionBody": AB_ADD_POWER_METER_CMD,
			"BgColor": BTN_BG_COLOR,
			"Image": ""
		},
		{
			"Columns": BTN_WIDTH_IN_COLUMNS,
			"Rows": BTN_HEIGHT_IN_ROWS,
			"Text": "<font color='{0}'>Додати ліч. по договору</font><br><br>".format(BTN_FONT_COLOR),
			"TextSize": "medium",
			"TextHAlign": "center",
			"TextVAlign": "center",
			"ActionType": "reply",
			"ActionBody": AB_ADD_POWER_METER_BY_CONTRACT_CMD,
			"BgColor": BTN_BG_COLOR,
			"Image": ""
		},
		{
			"Columns": BTN_WIDTH_IN_COLUMNS,
			"Rows": BTN_HEIGHT_IN_ROWS,
			"Text": "<font color='{0}'>Видалити лічильник</font><br><br>".format(BTN_FONT_COLOR),
			"TextSize": "medium",
			"TextHAlign": "center",
			"TextVAlign": "center",
			"ActionType": "reply",
			"ActionBody": AB_DELETE_POWER_METER_CMD,
			"BgColor": BTN_BG_COLOR,
			"Image": ""
		},

		{
			"Columns": BTN_WIDTH_IN_COLUMNS,
			"Rows": BTN_HEIGHT_IN_ROWS,
			"Text": "<font color='{0}'>Допомога</font><br><br>".format(BTN_FONT_COLOR),
			"TextSize": "medium",
			"TextHAlign": "center",
			"TextVAlign": "center",
			"ActionType": "reply",
			"ActionBody": AB_HELP_CMD,
			"BgColor": BTN_BG_COLOR,
			"Image": ""
		},

	
	]
}

to_main_menu_keyboard = {
	"Type": "keyboard",
	"Buttons": 
	[
		{
			"Columns": 6,
			"Rows": 1,
			"Text": "<font color='{0}'>Головне меню</font><br><br>".format(BTN_FONT_COLOR),
			"TextSize": "medium",
			"TextHAlign": "center",
			"TextVAlign": "center",
			"ActionType": "reply",
			"ActionBody": AB_MAIN_MENU_CMD,
			"BgColor": BTN_BG_COLOR,
			"Image": ""
		},
	]
}

start_keyboard = {
	"Type": "keyboard",
	"Buttons":
	[
		{
			"Columns": 6,
			"Rows": 1,
			"Text": "<font color='{0}'>Початок</font><br><br>".format(BTN_FONT_COLOR),
			"TextSize": "medium",
			"TextHAlign": "center",
			"TextVAlign": "center",
			"ActionType": "reply",
			"ActionBody": AB_START_CMD,
			"BgColor": BTN_BG_COLOR,
			"Image": ""
		},
	]
}

def create_keyboard_on_counter(counters):
	keyboard = \
	{
		"Type": "keyboard",
		"Buttons": 
		[
			{
				"Columns": 6,
				"Rows": 1,
				"Text": "<font color='{0}'>{1} {2} {3}</font><br><br>".format(BTN_FONT_COLOR, c.contract_number,c.counter_factory, c.owner_name),
				"TextSize": "medium",
				"TextHAlign": "center",
				"TextVAlign": "center",
				"ActionType": "reply",
				"ActionBody": "{uuid}".format(uuid=c.counter_uuid),
				"BgColor": BTN_BG_COLOR,
				"ReplyType": "message",
				"Image": ""
			}
		for c in  counters]
	}
	btn_main = {
			"Columns": 6,
			"Rows": 1,
			"Text": "<font color='{0}'>Головне меню</font><br><br>".format(BTN_FONT_COLOR),
			"TextSize": "medium",
			"TextHAlign": "center",
			"TextVAlign": "center",
			"ActionType": "reply",
			"ActionBody": AB_MAIN_MENU_CMD,
			"BgColor": BTN_BG_COLOR,
			"Image": ""
		}
	keyboard['Buttons'].append(btn_main)	
	return keyboard
	