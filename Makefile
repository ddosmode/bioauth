PREFIX ?= /usr/local
BINDIR ?= $(PREFIX)/bin
SYSCONFDIR ?= /etc/bioauth
PAMDIR ?= /usr/share/pam-configs

.PHONY: all test install uninstall

all: test

test:
	PYTHONPATH=. python3 -m unittest discover -s tests

install:
	install -d $(BINDIR)
	install -d $(SYSCONFDIR)
	install -d /var/lib/bioauth
	install -m 755 pam/bioauth-pam $(BINDIR)/bioauth-pam
	install -m 755 src/cli.py $(BINDIR)/bioauth
	if [ -d $(PAMDIR) ]; then install -m 644 pam/bioauth $(PAMDIR)/bioauth; fi

uninstall:
	rm -f $(BINDIR)/bioauth-pam
	rm -f $(BINDIR)/bioauth
	rm -f $(PAMDIR)/bioauth
