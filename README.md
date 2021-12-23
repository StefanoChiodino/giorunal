# Giournal - Encrypted ournaling on git 

Giournal is an encrypted journaling system, that use git to store your entries. This way you'll get cloud backup for free.

## Setup

The first time you use Giournal it will create a settings files `.giournal` under your home folder.

The process will ask if you want to store your password in the keychain, meaning you won't have to type it again. It will also offer to set up a remote git repository for your journal, where to store your entries, and what editor to use to add entries.

## Adding entries

### Using your configured editor

`python3 main.py --editor` will open your editor. Just save your file and close it when you are done. Giournal will encrypt it and push it to git.

### Manual entry

If you don't want to use an editor you can just type the text like `python3 main.py This will be your new entry`.

## Viewing your entries

You can use `python3 main.py --list` to list al the entries on the shell.

Alternatively use `python3 main.py --decrypt` to decrypt all your entries in place. Giournal will then wait for you to press enter to encrypt them again.

## Sync

By default Giournal will sync with git only when you add an entry. To sync manually run `python3 main.py --sync`