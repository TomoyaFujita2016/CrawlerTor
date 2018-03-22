import sys

INIT_PORT = 9050
SPAN = 2 # >=2
PORTS_FILE = "./ports"

if __name__=="__main__":
    args = sys.argv
    if len(args) < 2:
        print("[*]Please input the number of ports as an argument.")
        exit()
    
    if args[1].isdigit(): 
        portnum = int(args[1])
    else:
        print("[*]Please input as a numeral")
        exit()

    ports = { "Socket": [], "Control": [] }
    
    for i in range(portnum):
        ports["Socket"].append(INIT_PORT + i * 2)
        ports["Control"].append(ports["Socket"][i] + 1)
    
    with open(PORTS_FILE, "w") as f:
        for i in range(portnum):
            f.write(str(ports["Socket"][i]) + " " + str(ports["Control"][i]) + "\n")

    print("added " + str(portnum) + " port to " + PORTS_FILE)
