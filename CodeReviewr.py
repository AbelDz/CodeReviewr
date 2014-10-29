"""A plugin for Sublime Text 3 to assist in manual code reviews."""

__author__ = "Abel Diaz"
__email__ = "abel.diaz.cardona@gmail.com"

import sublime, sublime_plugin

class CodeReviewrCommand(sublime_plugin.TextCommand):

	trace = CodeTrace("CodeTrace") #TO DO: in the future it will support many Code Traces at the same time

	def __init__(self,view):
		self.window = None
		super(CodeReviewrCommand,self).__init__(view)
		
	def run(self,edit,mode="toggle"):
		self.window = self.view.window()
		output_panel = self.window.create_output_panel("CodeReveiwrLog")
		output_panel.set_read_only(False)

		if mode == "toggle":
			self.view.run_command("toggle_bookmark")		
			self.window.show_input_panel("Enter a label for the line >> ","",self.on_input_addlabel_done,None,None)
			#output_panel.insert(edit,output_panel.size(),"Line successfully added to trace")

		elif mode == "search":
			keys = CodeReviewrCommand.trace.get_formatted_keys()
			self.window.show_quick_panel(keys,self.on_line_select_done)
			output_panel.insert(edit,output_panel.size(),"Line successfully added to CodeReviewr")

		elif mode == "clear":
			CodeReviewrCommand.trace = None
			CodeReviewrCommand.trace = CodeTrace("CodeTrace")
			self.view.run_command("clear_bookmarks")
			output_panel.insert(edit,output_panel.size(),"CodeReviewr buffer cleared")
			#output_panel.insert(edit,output_panel.size(),str(row+1)) #output test line
			self.display_codereviewr_output()

	def on_input_addlabel_done(self, label): #generate CodeLine objects instead of just text
		path = self.view.file_name()
		position = self.view.sel()[0].begin()
		code = self.view.substr(self.view.line(position))
		(row,col) = self.view.rowcol(position)
		code_line = CodeLine(label,path,position,row+1,code)
		CodeReviewrCommand.trace.add(code_line)

	def on_line_select_done(self,selection): #once selected go to the line in the file
		selIndex = int(selection)
		selected_code_line = CodeReviewrCommand.trace.get_by_index(selIndex)
		file_to_open = str(selected_code_line.get_file_path())
		line_to_go = selected_code_line.get_line_no()

		file_view = self.window.open_file(file_to_open)
		while(file_view.is_loading()):
			pass

		file_view.run_command("goto_line", {"line": line_to_go} )
		
	def display_codereviewr_output(self):
		self.window.run_command("show_panel",{"panel": "output.CodeReveiwrLog"})




class CodeLine(): #a CodeTrace will be conformed of a list of this data structure
	
	def __init__(self,label,file_path,file_position,line_no,code):
		self.label = label
		self.file_path = file_path
		self.file_position = file_position
		self.lineNo = line_no
		self.code = code

	def get_label(self):
		return self.label

	def get_file_path(self):
		return self.file_path

	def get_line_no(self):
		return self.lineNo

	def get_code(self):
		return self.code

	def get_file_position(self):
		return self.file_position




class CodeTrace():
	
	def __init__(self,name):
		self.name = name
		self.code_lines = []

	def add(self,code_line):
		self.code_lines.append(code_line)

	def get_by_index(self,index):
		return self.code_lines[index]

	def get_formatted_keys(self): #this method will return the string array to populate the quick selection panel when searching within the trace
		keys = []
		for code_line in self.code_lines:
			label = str(code_line.get_label())
			line_no = str(code_line.get_line_no())
			code = str(code_line.get_code().strip()[:100])
			filename = str(code_line.get_file_path()[code_line.get_file_path().rfind("\\"):]) #TO DO: will only work for windows, fix for the rest of the platforms
			keys.append("\"" + label + "\" - FILE: " + filename + " LINE: " +line_no + ". " + code)
		return keys
		