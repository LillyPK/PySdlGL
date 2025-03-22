import sys
import sdl2
import sdl2.video
import sdl2.ext
from OpenGL.GL import *
from PIL import Image  # For PNG handling
import numpy as np

# Global state variables
image_x, image_y = 200, 200
moving = False
texture_id = None
popup_open = False  # Tracks if the File popup is open

# Initial window size
WINDOW_WIDTH, WINDOW_HEIGHT = 800, 600
TOP_BAR_HEIGHT = 40  # Height of the top bar

# Button positions (relative to window size, initial values will be adjusted)
file_button = {"x": 10, "y": 5, "width": 80, "height": 30, "label": "File"}
settings_button = {"x": WINDOW_WIDTH - 90, "y": 5, "width": 80, "height": 30, "label": "Settings"}

def load_texture(image_path):
    """Loads a PNG image and converts it into an OpenGL texture."""
    img = Image.open(image_path)
    img = img.transpose(Image.FLIP_TOP_BOTTOM)  # Flip to match OpenGL coordinates
    img_data = np.array(img.convert("RGBA"), dtype=np.uint8)

    tex_id = glGenTextures(1)
    glBindTexture(GL_TEXTURE_2D, tex_id)

    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)

    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, img.width, img.height, 0, GL_RGBA, GL_UNSIGNED_BYTE, img_data)
    
    return tex_id, img.width, img.height

def draw_rectangle(x, y, width, height, color):
    """Draws a filled rectangle with OpenGL."""
    glColor3f(*color)
    glBegin(GL_QUADS)
    glVertex2f(x, y)
    glVertex2f(x + width, y)
    glVertex2f(x + width, y + height)
    glVertex2f(x, y + height)
    glEnd()

def render_texture(texture, x, y, width, height):
    """Renders an OpenGL texture at a given position."""
    glEnable(GL_TEXTURE_2D)
    glBindTexture(GL_TEXTURE_2D, texture)
    glColor3f(1, 1, 1)

    glBegin(GL_QUADS)
    glTexCoord2f(0, 0); glVertex2f(x, y)
    glTexCoord2f(1, 0); glVertex2f(x + width, y)
    glTexCoord2f(1, 1); glVertex2f(x + width, y + height)
    glTexCoord2f(0, 1); glVertex2f(x, y + height)
    glEnd()

    glDisable(GL_TEXTURE_2D)

def draw_text(x, y, text):
    """Basic text rendering using OpenGL rasterization (Optional: Use SDL_ttf for better fonts)."""
    glColor3f(1, 1, 1)
    glRasterPos2f(x, y)
    for char in text:
        sdl2.SDL_GL_RenderText(ord(char))

def handle_events():
    """Handles SDL2 events for user input."""
    global moving, image_x, image_y, popup_open, WINDOW_WIDTH, WINDOW_HEIGHT, file_button, settings_button

    event = sdl2.SDL_Event()
    while sdl2.SDL_PollEvent(event):
        if event.type == sdl2.SDL_QUIT:
            return False

        elif event.type == sdl2.SDL_MOUSEBUTTONDOWN:
            x, y = event.button.x, event.button.y

            # Check if File button is clicked
            if file_button["x"] <= x <= file_button["x"] + file_button["width"] and \
               file_button["y"] <= y <= file_button["y"] + file_button["height"]:
                popup_open = not popup_open  # Toggle popup
            
            # Check if Settings button is clicked
            if settings_button["x"] <= x <= settings_button["x"] + settings_button["width"] and \
               settings_button["y"] <= y <= settings_button["y"] + settings_button["height"]:
                print("Settings clicked (Functionality not implemented)")

        elif event.type == sdl2.SDL_KEYDOWN:
            if event.key.keysym.sym == sdl2.SDLK_g:  # Press G to start moving
                moving = True
            elif event.key.keysym.sym == sdl2.SDLK_RETURN:  # Press Enter to set position
                moving = False

        elif event.type == sdl2.SDL_MOUSEMOTION and moving:
            image_x, image_y = event.motion.x, event.motion.y
        
        # Handle window resize
        elif event.type == sdl2.SDL_WINDOWEVENT:
            if event.window.event == sdl2.SDL_WINDOWEVENT_SIZE_CHANGED:
                WINDOW_WIDTH = event.window.data1
                WINDOW_HEIGHT = event.window.data2

                # Update projection matrix for the new window size
                glViewport(0, 0, WINDOW_WIDTH, WINDOW_HEIGHT)
                glMatrixMode(GL_PROJECTION)
                glLoadIdentity()
                glOrtho(0, WINDOW_WIDTH, WINDOW_HEIGHT, 0, -1, 1)
                glMatrixMode(GL_MODELVIEW)

                # Recalculate button positions relative to the new window size
                file_button["x"] = int(WINDOW_WIDTH * 0.01)
                settings_button["x"] = int(WINDOW_WIDTH * 0.99) - settings_button["width"]

    return True

def main():
    global texture_id, image_x, image_y

    # Initialize SDL2
    if sdl2.SDL_Init(sdl2.SDL_INIT_VIDEO) != 0:
        print("SDL2 could not initialize:", sdl2.SDL_GetError().decode())
        return

    window = sdl2.SDL_CreateWindow(
        b"SDL2 + OpenGL Image Movement",
        sdl2.SDL_WINDOWPOS_CENTERED, sdl2.SDL_WINDOWPOS_CENTERED,
        WINDOW_WIDTH, WINDOW_HEIGHT,
        sdl2.SDL_WINDOW_OPENGL | sdl2.SDL_WINDOW_RESIZABLE
    )

    if not window:
        print("Could not create window:", sdl2.SDL_GetError().decode())
        return

    # Create OpenGL context
    context = sdl2.SDL_GL_CreateContext(window)
    if not context:
        print("Could not create OpenGL context:", sdl2.SDL_GetError().decode())
        return

    # Load image as texture
    texture_id, img_width, img_height = load_texture("your_image.png")

    # OpenGL setup
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    glOrtho(0, WINDOW_WIDTH, WINDOW_HEIGHT, 0, -1, 1)
    glMatrixMode(GL_MODELVIEW)

    running = True
    while running:
        running = handle_events()

        glClear(GL_COLOR_BUFFER_BIT)

        # Draw the top bar
        draw_rectangle(0, 0, WINDOW_WIDTH, TOP_BAR_HEIGHT, (0.2, 0.2, 0.2))  # Dark gray bar

        # Draw the buttons
        draw_rectangle(file_button["x"], file_button["y"], file_button["width"], file_button["height"], (0.3, 0.3, 0.3))
        draw_rectangle(settings_button["x"], settings_button["y"], settings_button["width"], settings_button["height"], (0.3, 0.3, 0.3))

        # Draw the popup if opened
        if popup_open:
            draw_rectangle(50, 50, 200, 100, (0.1, 0.1, 0.1))  # Simple popup background

        # Render the image
        render_texture(texture_id, image_x, image_y, img_width, img_height)

        sdl2.SDL_GL_SwapWindow(window)

    # Cleanup
    glDeleteTextures([texture_id])
    sdl2.SDL_GL_DeleteContext(context)
    sdl2.SDL_DestroyWindow(window)
    sdl2.SDL_Quit()

if __name__ == "__main__":
    main()
