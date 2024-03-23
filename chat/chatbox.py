import pygame
import pygame_gui

from pygame_gui import UIManager, UI_TEXT_ENTRY_CHANGED,UI_BUTTON_PRESSED
from pygame_gui.elements import UIWindow, UITextEntryBox, UITextBox, UIButton
from network import Network
import socket, threading

pygame.init()


pygame.display.set_caption('Pygame Notepad')
window_surface = pygame.display.set_mode((400, 660))
manager = UIManager((400, 700), 'data/themes/chat.json')

background = pygame.Surface((400, 700))
background.fill(manager.ui_theme.get_colour('dark_bg'))


#notepad_window = UIWindow(pygame.Rect(50, 20, 300, 400), window_display_title="Pygame Notepad")

#output_window = UIWindow(pygame.Rect(400, 20, 300, 400), window_display_title="Pygame GUI Formatted Text")

# swap to editable text box
text_entry_box = UITextEntryBox(
        #relative_rect=pygame.Rect((0, 0), notepad_window.get_container().get_size()),
        relative_rect=pygame.Rect(14, 489, 300, 100),
        initial_text="",
        #container=notepad_window)
        )

text_output_box = UITextBox(
        #relative_rect=pygame.Rect((0, 0), output_window.get_container().get_size()),
        relative_rect=pygame.Rect(14, 14, 300, 400),
        html_text="",
        #container=output_window)
        )

forfeit_button = UIButton(
        relative_rect=pygame.Rect(14, 590, 100, 70),
        text="Forfeit",
        manager=manager,
        tool_tip_text="",
        object_id='#forfeit_button'
        )

tie_button = UIButton(
        relative_rect=pygame.Rect(114, 590, 100, 70),
        text="Tie",
        manager=manager,
        tool_tip_text="",
        object_id='#tie_button'
        )

last_time = pygame.time.get_ticks()
caret_position = 0

running = True
def handle_messages(connection: socket.socket):
    '''
        Receive messages sent by the server and display them to user
    '''

    while running:
        try:
            msg = connection.recv(1024)

            # If there is no message, there is a chance that connection has closed
            # so the connection will be closed and an error will be displayed.
            # If not, it will try to decode message in order to show to user.
            if msg:
                #print(msg.decode())
                text_output_box.append_html_text(msg.decode() + "<br><br>")
            else:
                connection.close()
                break

        except Exception as e:
            print(f'Error handling message from server: {e}')
            connection.close()
            break


    connection.close()
    exit()

data = ""
reply = ""
SERVER_ADDRESS = '127.0.0.1'
SERVER_PORT = 12000

try:
    # Instantiate socket and start connection with server
    socket_instance = socket.socket()
    socket_instance.connect((SERVER_ADDRESS, SERVER_PORT))
    # Create a thread in order to handle messages sent by server
    threading.Thread(target=handle_messages, args=[socket_instance]).start()

    print('Connected to chat!')


except Exception as e:
    print(f'Error connecting to server socket {e}')
    socket_instance.close()


clock = pygame.time.Clock()
is_running = True


while is_running:
    time_delta = clock.tick(60)/1000.0
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            is_running = False
            running = False
            socket_instance.shutdown(socket.SHUT_WR)
            exit()

        # if event.type == UI_TEXT_EwNTRY_CHANGED and event.ui_element == text_entry_box:
        #     text_output_box.set_text(event.text)

        if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
            text_output_box.append_html_text("You" + ": " + text_entry_box.get_text() + "<br><br>")
            # data = str(net.id) + ":" + text_entry_box.get_text()
            # reply = parse_data(net.send(data))
            socket_instance.send(text_entry_box.get_text().encode())
            text_entry_box.clear()
            pygame.event.post(pygame.event.Event(pygame.KEYDOWN, unicode="U+232B", key=pygame.K_BACKSPACE, mod=pygame.KMOD_NONE))

        if event.type == pygame_gui.UI_BUTTON_PRESSED:
            if event.ui_element == forfeit_button:
                text_output_box.append_html_text("--Forfeit Request--" + "<br><br>")
                socket_instance.send("/forfeit".encode())

        # if reply != "":
        #     text_output_box.append_html_text("Opponent:" + reply + "<br><br>")


        manager.process_events(event)
    # current_time = pygame.time.get_ticks()
    # if current_time - last_time >= 1000:  # 1000 milliseconds = 1 second
    #     x, y = pygame.mouse.get_pos()
    #     print(x, y)
    #     last_time = current_time


    manager.update(time_delta)

    window_surface.blit(background, (0, 0))
    manager.draw_ui(window_surface)

    pygame.display.update()

