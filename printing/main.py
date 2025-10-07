from loginPage import create_main_menu
from printingAlly import create_printing_menu
from clientCalls import loggedOut

if __name__ == "__main__":
    active = True
    while active:
        loggedEmployee = create_main_menu()
        if loggedEmployee is None:
            active = False
        else:
            # Assume create_printing_menu returns True if user wants to continue, False to exit
            continue_running = create_printing_menu(loggedEmployee)
            if continue_running is False:
                active = False  # Stop the loop if the user closes the printing menu
            else:
                try:
                    response = loggedOut(
                        loggedEmployee.employeeName,
                        server_ip="192.168.111.230",
                        port=8080
                    )
                    if response.get("status") != "success":
                        show_custom_popup(
                            "Logout Error",
                            message=response.get("message", "Failed to log out")
                        )
                except Exception as e:
                    show_custom_popup("Connection Error", message=str(e))
