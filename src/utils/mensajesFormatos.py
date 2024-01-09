from termcolor import colored

def print_color(message, color='white'):
    """
    Imprime un mensaje con el color especificado.

    Args:
        message (str): El mensaje a imprimir.
        color (str): El color a utilizar (por defecto es 'white').

    Returns:
        None
    """
    print(colored(message, color))
    
def printWarning(message):
    print_color(message=f'WARNING: {message}',color='red')
    
def printInfoSuccesful(message):
    print_color(message=f'INFO: {message}',color='green')