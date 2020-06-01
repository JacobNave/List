from tkinter import *
import sqlite3

root = Tk()
root.title("Shopping List")
root.geometry('300x400')

listFrame = Frame(root)

#Selected items from the list
#contains dictionary for each entry with name, quantity, cost, id, and if its selected
selected_list= []

#True if an add or edit window is open, prevents more than 2 windows
window_open = False

#Bottom bar info variables
item_count = StringVar()
total_cost = StringVar()
item_count.set("Number of Items: 0")
total_cost.set("Total Cost: $0.00")


#FUNCTIONS

#create db table
'''
def createTable():
	conn = sqlite3.connect("shopping_list.db")

	c = conn.cursor()

	c.execute("""CREATE TABLE listItems (
		name text,
		quantity text,
		cost real
		)""")

	conn.commit()
	conn.close()
'''

#add an item to the db
def insert(name, quantity, cost, window):
	conn = sqlite3.connect("shopping_list.db")

	c = conn.cursor()

	c.execute("INSERT INTO listItems VALUES (:name, :quantity, :cost)",
			{
				"name": name,
				'quantity': quantity,
				'cost': cost
			})

	conn.commit()
	conn.close()
	updateListWindow()
	window.destroy()

def update(name, quantity, cost, item_id, window):
	conn = sqlite3.connect("shopping_list.db")

	c = conn.cursor()

	c.execute("UPDATE listItems SET name = :name, quantity = :quantity, cost = :cost WHERE oid = :item_id",
			{
				"name": name,
				'quantity': quantity,
				'cost': cost,
				'item_id': item_id
			})

	conn.commit()
	conn.close()
	updateListWindow()
	window.destroy()


def editItemInDatabase(name, quantity, cost, id):
	edit_window = Toplevel()
	edit_window.title('Edit Item')	

	global edit_name_var
	global edit_quantity_var
	global edit_cost_var
	global edit_name_label
	global edit_quantity_label
	global edit_cost_label

	#variables
	

	edit_name_var = StringVar()
	edit_quantity_var = IntVar()
	edit_cost_var = DoubleVar()

	edit_name_var.set(name)
	edit_quantity_var.set(quantity)
	edit_cost_var.set(cost)


	#make widgets
	edit_name_entry = Entry(edit_window, width = 30, textvariable =edit_name_var)
	edit_quantity_entry = Entry(edit_window, width = 30, textvariable =edit_quantity_var)
	edit_cost_entry = Entry(edit_window, width = 30, textvariable =edit_cost_var)

	edit_name_label = Label(edit_window, text="Name: ")
	edit_quantity_label = Label(edit_window, text="Quantity: ")
	edit_cost_label = Label(edit_window, text="Cost: $")

	edit_item = Button(edit_window, text='Finish Edits', command=lambda: update(edit_name_var.get(), edit_quantity_var.get(), edit_cost_var.get(), id, edit_window))

	#place widgets
	edit_name_label.grid(row =1, column=0)
	edit_quantity_label.grid(row =2, column=0)
	edit_cost_label.grid(row =3, column=0)

	edit_name_entry.grid(row =1, column=1)
	edit_quantity_entry.grid(row =2, column=1)
	edit_cost_entry.grid(row =3, column=1)
	edit_item.grid(row=4, column=0, columnspan=2)






#Adds a shopping item to list
def addItem(frame, name, quantity, cost, id, checkVar):
	#create widgets
	row_frame = Frame(frame, width=300)
	row_check = Checkbutton(row_frame, variable = checkVar, onvalue=1, offvalue=0)
	info_label = Label(row_frame, text= (str(quantity) + 'x ' + name))
	cost_label = Label(row_frame, text= ("${:0.2f}".format(cost)))
	edit_button = Button(row_frame, text='Edit', command=lambda: editItemInDatabase(name, quantity, cost, id))

	#place widgets
	row_check.pack(side=LEFT)
	edit_button.pack(side=RIGHT)
	cost_label.pack(side=RIGHT)
	info_label.pack(side=LEFT, fill=X)
	row_frame.pack(fill=X, anchor=N)

#add all items in the database to the frame
def addAllItems(frame):
	conn = sqlite3.connect("shopping_list.db")

	c = conn.cursor()
	#get all items in list including id in last position
	c.execute("SELECT *, oid FROM listItems")
	records = c.fetchall()

	conn.commit()
	conn.close()

	for record in records:
		itemDict = {
			'name': record[0],
			'quantity': record[1],
			'cost': record[2],
			'id': record[3],
			'selected': IntVar()
		}
		selected_list.append(itemDict)
		addItem(frame, record[0], record[1], record[2], record[3], itemDict['selected'])


#delete selected items
def delete():
	to_remove = []
	for item in selected_list:
		if (item['selected'].get() == 1):
			to_remove.append(item['id'])

	conn = sqlite3.connect("shopping_list.db")

	c = conn.cursor()

	for item_id in to_remove:
		c.execute("DELETE FROM listItems WHERE oid = :item_id", {'item_id': item_id})

	conn.commit()
	conn.close()
	updateListWindow()



#opens new window to create an item
def addToDatabase():
	add_window = Toplevel()
	add_window.title('Add Item')	

	global name_var
	global quantity_var
	global cost_var
	global name_label
	global quantity_label
	global cost_label

	#variables
	

	name_var = StringVar()
	quantity_var = IntVar()
	cost_var = DoubleVar()

	#make widgets
	name_entry = Entry(add_window, width = 30, textvariable =name_var)
	quantity_entry = Entry(add_window, width = 30, textvariable =quantity_var)
	cost_entry = Entry(add_window, width = 30, textvariable =cost_var)

	name_label = Label(add_window, text="Name: ")
	quantity_label = Label(add_window, text="Quantity: ")
	cost_label = Label(add_window, text="Cost: $")

	add_new = Button(add_window, text='Add Item to List', command=lambda: insert(name_var.get(), quantity_var.get(), cost_var.get(), add_window))

	#place widgets
	name_label.grid(row =1, column=0)
	quantity_label.grid(row =2, column=0)
	cost_label.grid(row =3, column=0)

	name_entry.grid(row =1, column=1)
	quantity_entry.grid(row =2, column=1)
	cost_entry.grid(row =3, column=1)
	add_new.grid(row=4, column=0, columnspan=2)



def updateListWindow():
	for child in listFrame.winfo_children():
		child.destroy()
	global selected_list
	selected_list = []
	addAllItems(listFrame)

	items = 0
	for item in selected_list:
		items += int(item['quantity'])
	item_count.set("Number of Items: " + str(items))

	cost = 0.0
	for item in selected_list:
		cost += (float(item['cost'])*float(item['quantity']))
	total_cost.set("Total Cost: ${:0.2f}".format(cost))



add_button = Button(root, text='Add Item', command=addToDatabase)


#bottom bar setup

bottom_frame = Frame(root)
item_count_label = Label(bottom_frame, textvariable=item_count)
total_cost_label = Label(bottom_frame, textvariable=total_cost)
delete_button = Button(bottom_frame, text='Delete', command = delete, padx = 45, pady = 15)



#add all list items
updateListWindow()



#place bottom bar
listFrame.pack(fill=BOTH)
delete_button.grid(row = 1, column=0, rowspan=2)
item_count_label.grid(row=1, column=1, columnspan=2, sticky=W)
total_cost_label.grid(row=2, column=1, columnspan=2, sticky=W)
bottom_frame.pack(fill=X, side=BOTTOM)
add_button.pack(fill=X, side=BOTTOM)


root.mainloop()