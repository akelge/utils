SRC = wrapper.c
EXEC = wrapper
INSTALLDIR = /usr/local/bin

all: $(EXEC)

clean:
	@rm -f $(EXEC)

install: all
	@echo Execing sudo, type your password
	@sudo -k
	@sudo cp $(EXEC) $(INSTALLDIR)
	@echo Copied to $(INSTALLDIR)
	@sudo chown 0:0 $(INSTALLDIR)/$(EXEC)
	@sudo chmod a+s $(INSTALLDIR)/$(EXEC)
	@echo Permission set

uninstall:
	@echo Execing sudo, type your password
	@sudo -k
	@sudo rm -f $(INSTALLDIR)/$(EXEC)
	@echo Unlinked
