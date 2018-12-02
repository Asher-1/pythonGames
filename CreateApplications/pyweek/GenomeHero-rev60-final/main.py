import tartley.main
def main():
    tartley.main.main()
    
if __name__ == "__main__":
	import cProfile
	command = """tartley.main.main()"""
	cProfile.runctx( command, globals(), locals(), filename="gnhero.profile" )
    
# vim: set filetype=python sts=4 sw=4 noet si :
