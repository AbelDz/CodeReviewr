"""A plugin for Sublime Text 3 to assist in manual code reviews."""

__author__ = "Abel Diaz"
__email__ = "abel.diaz.cardona@gmail.com"

import sublime, sublime_plugin

class CodeLine: #a CodeTrace will be conformed of a list of this data structure
	
	def __init__(self,label,file_path,file_position,line_no,code,physical_file,view):
		self.label = label
		self.file_path = file_path
		self.file_position = file_position
		self.lineNo = line_no
		self.code = code
		self.physical_file = physical_file
		self.view = view

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

	def is_in_physical_file(self):
		return self.physical_file

class CodeTrace:
	
	def __init__(self,name):
		self.name = name
		self.code_lines = []

	def add(self,code_line):
		self.code_lines.append(code_line)

	def get_count(self):
		return len(self.code_lines)

	def get_by_index(self,index):
		return self.code_lines[index]

	def get_name(self):
		return self.name

	def get_formatted_keys(self): #this method will return the string array to populate the quick selection panel when searching within the CodeTrace
		keys = []
		for code_line in self.code_lines:
			label = str(code_line.get_label())
			line_no = str(code_line.get_line_no())
			code = str(code_line.get_code().strip()[:100])
			filename = "BufferedFile"
			if code_line.is_in_physical_file():
				file_path = code_line.get_file_path()
				path_separator = "/"
				if "\\" in file_path: #if it's a Windows path
					path_separator = "\\"
				filename = str(file_path[file_path.rfind(path_separator):]) 
			keys.append("\"" + label + "\" - FILE: " + filename + " LINE: " +line_no + ". " + code)
		return keys

class CodeReviewrCommand(sublime_plugin.TextCommand):

	traces = []
	currentTrace = None

	def __init__(self,view):
		self.window = None
		super(CodeReviewrCommand,self).__init__(view)
		
	def run(self,edit,mode="toggle"):
		self.window = self.view.window()
		output_panel = self.window.create_output_panel("CodeReveiwrLog")
		output_panel.set_read_only(False)

		if mode == "toggle":
			self.toggle_line()

		elif mode == "select_line":
			self.select_line()

		elif mode == "new_trace":
			self.new_trace()

		elif mode == "select_trace":
			self.select_trace()

		elif mode == "clear":
			CodeReviewrCommand.traces = None
			CodeReviewrCommand.currentTrace = None
			CodeReviewrCommand.traces = []
			self.view.run_command("clear_bookmarks")
			output_panel.insert(edit,output_panel.size(),"CodeReviewr buffer cleared")
			self.display_codereviewr_output()

	def toggle_line(self):
		if CodeReviewrCommand.currentTrace != None:
			self.view.run_command("toggle_bookmark")		
			self.window.show_input_panel("Enter a label for the line >> ","",self.on_input_toggleline_done,None,None)

	def select_line(self):
		if (CodeReviewrCommand.currentTrace != None) and (CodeReviewrCommand.currentTrace.get_count() > 0):
			keys = CodeReviewrCommand.currentTrace.get_formatted_keys()
			self.window.show_quick_panel(keys,self.on_line_select_done)

	def new_trace(self):
		self.window.show_input_panel("NEW TRACE >> ","",self.on_input_newtrace_done,None,None)

	def select_trace(self):
		if len(CodeReviewrCommand.traces) > 0:
			keys = self.get_traces_keys()
			self.window.show_quick_panel(keys,self.on_trace_select_done)

	def get_traces_keys(self):
		keys = []
		for trace in CodeReviewrCommand.traces:
			keys.append(trace.get_name())
		return keys

	def on_trace_select_done(self,selection):
		CodeReviewrCommand.currentTrace = CodeReviewrCommand.traces[selection]

	def on_input_newtrace_done(self,name):
		if name != "":
			trace = CodeTrace(name)
			CodeReviewrCommand.traces.append(trace)
			CodeReviewrCommand.currentTrace = trace

	def on_input_toggleline_done(self, label): #Once the label is entered, create a CodeLine object and add it to the CodeTrace
		path = self.view.file_name()
		physical_file = True

		if path == None:
			physical_file = False

		line_view = self.view
		position = self.view.sel()[0].begin()
		code = self.view.substr(self.view.line(position))
		(row,col) = self.view.rowcol(position)
		code_line = CodeLine(label,path,position,row+1,code,physical_file,line_view)
		CodeReviewrCommand.currentTrace.add(code_line)

	def on_line_select_done(self,selection): #once selected go to the line in the file
		selIndex = int(selection)
		selected_code_line = CodeReviewrCommand.currentTrace.get_by_index(selIndex)
		line_to_go = selected_code_line.get_line_no()
		file_to_open = selected_code_line.get_file_path()
		is_physical_file = selected_code_line.is_in_physical_file()
		file_view = None
		
		if is_physical_file: #if it's a physical file
			file_view = self.window.open_file(file_to_open)
			while(file_view.is_loading()):
				pass
		else:				 #if it's only a buffered file
			file_view = file_to_open
			self.window.focus_view(file_view)

		file_view.run_command("goto_line", {"line": line_to_go} )
		
	def display_codereviewr_output(self):
		self.window.run_command("show_panel",{"panel": "output.CodeReveiwrLog"})

