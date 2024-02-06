from threading import Thread
from time import sleep
import click

@click.group(chain=True)
def cli():
    pass

@cli.command()
def initdb():
    click.echo('Initialized the database')

@cli.command()
def dropdb():
    click.echo('Dropped the database')

def always_sleep():
    while True:
        sleep(10)


if __name__ == '__main__':
    # t = Thread(target=cli, daemon=True)
    # t.start()
    # always_sleep()
    [1].index(2)
