#/* UART INSTRUCTION SET  (3 bits)    
#0x0: 0: read register       
#0x1: 1: read memory         
#0x3: 2: write register (im not working on this right now just change te memory to set a register then move to that place in memory by changing pc)
#0x3: 3: write memory
#0x4: 4: halt
#0x5: 5: run                 
#0x6: 6: set memreg  high    
#0x7: 7: set memreg  low     
# gotta send a "@" ack bit first then send your appropriate data
#[15:13] opcode
#[12]    high/low selector for some commands
#[11:8]   unused
#[7:0]   data byte

#/*
#Registers
#0: zero (always holds zero) => zero // Restricted
#1: load reg => r1// Restricted
#2: argument 0 / return value => r2
#3: argument 1 => r3
#4: temporary => r4
#5: temporary => r5
#6: stack pointer (uninitialized by default) => sp //not restricted but important to use safely
#7: return address => ra //restricted
#
#Instruction Set
#0:ld => load
#1:st => store
#2:add
#3:sub
#4:mul
#5:div
#6:mod
#7:and
#8:or
#9:not
#10:nand
#11:nor
#12:xor
#13:be => branch if equal (beq RC,RA, (RB)) RB is the destination
#14:bne => branch if not equal
#15:blt => branch if less than
#16:bgt => branch if greater than
#17:sl => shift L
#18:sr => shift R
#19:li => load immdiate into r1
#20:jmp => jump (jump (rc)) jump to rc
#21:mv => move
#22:call (call (ra)) basically jump but keep track of this position
#23:ret


import serial
import subprocess
from serial.tools import list_ports
from pathlib import Path


def bits_to_reg(bits):
    bits = bits.lower()
    if bits == "000":
        return "zero"
    elif bits == "001":
        return "r1"
    elif bits == "010":
        return "r2"
    elif bits == "011":
        return "r3"
    elif bits == "100":
        return "r4"
    elif bits == "101":
        return "r5"
    elif bits == "110":
        return "sp"
    elif bits == "111":
        return "ra"
    else:
        return "unknown"


def reg_to_bits(reg):
    reg = reg.lower()
    if reg == "zero" or reg == "r0":
        return "000"
    elif reg == "r1":
        return "001"
    elif reg == "r2":
        return "010"
    elif reg == "r3":
        return "011"
    elif reg == "r4":
        return "100"
    elif reg == "r5":
        return "101"
    elif reg == "sp" or reg == "r6":
        return "110"
    elif reg == "ra" or reg == "r7":
        return "111"
    else:
        return "000"


def disassemble(line):
    line = line.strip()
    if len(line) != 16 or any(bit not in "01" for bit in line):
        return "invalid instruction"

    op = int(line[-5:], 2)

    match op:
        case 0:
            rb = bits_to_reg(line[5:8])
            ra = bits_to_reg(line[8:11])
            return f"ld {ra}, ({rb})"
        case 1:
            rb = bits_to_reg(line[5:8])
            ra = bits_to_reg(line[8:11])
            return f"st {ra}, ({rb})"
        case 2:
            rc = bits_to_reg(line[2:5])
            rb = bits_to_reg(line[5:8])
            ra = bits_to_reg(line[8:11])
            return f"add {ra}, {rb}, {rc}"
        case 3:
            rc = bits_to_reg(line[2:5])
            rb = bits_to_reg(line[5:8])
            ra = bits_to_reg(line[8:11])
            return f"sub {ra}, {rb}, {rc}"
        case 4:
            rc = bits_to_reg(line[2:5])
            rb = bits_to_reg(line[5:8])
            ra = bits_to_reg(line[8:11])
            return f"mul {ra}, {rb}, {rc}"
        case 5:
            rc = bits_to_reg(line[2:5])
            rb = bits_to_reg(line[5:8])
            ra = bits_to_reg(line[8:11])
            return f"div {ra}, {rb}, {rc}"
        case 6:
            rc = bits_to_reg(line[2:5])
            rb = bits_to_reg(line[5:8])
            ra = bits_to_reg(line[8:11])
            return f"mod {ra}, {rb}, {rc}"
        case 7:
            rc = bits_to_reg(line[2:5])
            rb = bits_to_reg(line[5:8])
            ra = bits_to_reg(line[8:11])
            return f"and {ra}, {rb}, {rc}"
        case 8:
            rc = bits_to_reg(line[2:5])
            rb = bits_to_reg(line[5:8])
            ra = bits_to_reg(line[8:11])
            return f"or {ra}, {rb}, {rc}"
        case 9:
            rb = bits_to_reg(line[5:8])
            ra = bits_to_reg(line[8:11])
            return f"not {ra}, {rb}"
        case 10:
            rc = bits_to_reg(line[2:5])
            rb = bits_to_reg(line[5:8])
            ra = bits_to_reg(line[8:11])
            return f"nand {ra}, {rb}, {rc}"
        case 11:
            rc = bits_to_reg(line[2:5])
            rb = bits_to_reg(line[5:8])
            ra = bits_to_reg(line[8:11])
            return f"nor {ra}, {rb}, {rc}"
        case 12:
            rc = bits_to_reg(line[2:5])
            rb = bits_to_reg(line[5:8])
            ra = bits_to_reg(line[8:11])
            return f"xor {ra}, {rb}, {rc}"
        case 13:
            rc = bits_to_reg(line[2:5])
            rb = bits_to_reg(line[5:8])
            ra = bits_to_reg(line[8:11])
            return f"beq {ra}, {rb}, ({rc})"
        case 14:
            rc = bits_to_reg(line[2:5])
            rb = bits_to_reg(line[5:8])
            ra = bits_to_reg(line[8:11])
            return f"bne {ra}, {rb}, ({rc})"
        case 15:
            rc = bits_to_reg(line[2:5])
            rb = bits_to_reg(line[5:8])
            ra = bits_to_reg(line[8:11])
            return f"blt {ra}, {rb}, ({rc})"
        case 16:
            rc = bits_to_reg(line[2:5])
            rb = bits_to_reg(line[5:8])
            ra = bits_to_reg(line[8:11])
            return f"bgt {ra}, {rb}, ({rc})"
        case 17:
            rc = bits_to_reg(line[2:5])
            rb = bits_to_reg(line[5:8])
            ra = bits_to_reg(line[8:11])
            return f"sl {ra}, {rb}, {rc}"
        case 18:
            rc = bits_to_reg(line[2:5])
            rb = bits_to_reg(line[5:8])
            ra = bits_to_reg(line[8:11])
            return f"sr {ra}, {rb}, {rc}"
        case 19:
            immediate = int(line[:-5], 2)
            return f"li {immediate}"
        case 20:
            ra = bits_to_reg(line[8:11])
            return f"jmp {ra}"
        case 21:
            src = bits_to_reg(line[5:8])
            dst = bits_to_reg(line[8:11])
            return f"mv {src}, {dst}"
        case 22:
            ra = bits_to_reg(line[8:11])
            return f"call {ra}"
        case 23:
            return "ret"
        case _:
            return "unknown instruction"


def assemble(input_file, output_file):
    folder = Path(__file__).resolve().parent
    input_path = Path(input_file)
    output_path = Path(output_file)
    if not input_path.is_absolute():
        input_path = folder / input_path
    if not output_path.is_absolute():
        output_path = folder / output_path

    with input_path.open("r", encoding="utf-8") as source, output_path.open("w", encoding="utf-8") as out:
        for line in source:
            line = line.strip()
            if not line or line.startswith("#"):
                continue

            args = line.split()
            match args[0].lower():
                case "ld":
                    ra = args[1].replace(",", "")
                    rb = args[2].replace("(", "").replace(")", "")
                    binRA = reg_to_bits(ra)
                    binRB = reg_to_bits(rb)
                    out.write("00000" + binRB + binRA + format(0, "05b") + "\n")

                case "st":
                    ra = args[1].replace(",", "")
                    rb = args[2].replace("(", "").replace(")", "")
                    binRA = reg_to_bits(ra)
                    binRB = reg_to_bits(rb)
                    out.write("00000" + binRB + binRA + format(1, "05b") + "\n")

                case "add":
                    ra = args[1].replace(",", "")
                    rb = args[2].replace(",", "")
                    rc = args[3].replace(",", "")
                    binRA = reg_to_bits(ra)
                    binRB = reg_to_bits(rb)
                    binRC = reg_to_bits(rc)
                    out.write("00" + binRC + binRB + binRA + format(2, "05b") + "\n")

                case "sub":
                    ra = args[1].replace(",", "")
                    rb = args[2].replace(",", "")
                    rc = args[3].replace(",", "")
                    binRA = reg_to_bits(ra)
                    binRB = reg_to_bits(rb)
                    binRC = reg_to_bits(rc)
                    out.write("00" + binRC + binRB + binRA + format(3, "05b") + "\n")

                case "mul":
                    ra = args[1].replace(",", "")
                    rb = args[2].replace(",", "")
                    rc = args[3].replace(",", "")
                    binRA = reg_to_bits(ra)
                    binRB = reg_to_bits(rb)
                    binRC = reg_to_bits(rc)
                    out.write("00" + binRC + binRB + binRA + format(4, "05b") + "\n")

                case "div":
                    ra = args[1].replace(",", "")
                    rb = args[2].replace(",", "")
                    rc = args[3].replace(",", "")
                    binRA = reg_to_bits(ra)
                    binRB = reg_to_bits(rb)
                    binRC = reg_to_bits(rc)
                    out.write("00" + binRC + binRB + binRA + format(5, "05b") + "\n")

                case "mod":
                    ra = args[1].replace(",", "")
                    rb = args[2].replace(",", "")
                    rc = args[3].replace(",", "")
                    binRA = reg_to_bits(ra)
                    binRB = reg_to_bits(rb)
                    binRC = reg_to_bits(rc)
                    out.write("00" + binRC + binRB + binRA + format(6, "05b") + "\n")

                case "and":
                    ra = args[1].replace(",", "")
                    rb = args[2].replace(",", "")
                    rc = args[3].replace(",", "")
                    binRA = reg_to_bits(ra)
                    binRB = reg_to_bits(rb)
                    binRC = reg_to_bits(rc)
                    out.write("00" + binRC + binRB + binRA + format(7, "05b") + "\n")

                case "or":
                    ra = args[1].replace(",", "")
                    rb = args[2].replace(",", "")
                    rc = args[3].replace(",", "")
                    binRA = reg_to_bits(ra)
                    binRB = reg_to_bits(rb)
                    binRC = reg_to_bits(rc)
                    out.write("00" + binRC + binRB + binRA + format(8, "05b") + "\n")

                case "not":
                    ra = args[1].replace(",", "")
                    rb = args[2].replace(",", "")
                    binRA = reg_to_bits(ra)
                    binRB = reg_to_bits(rb)
                    out.write("00000" + binRB + binRA + format(9, "05b") + "\n")

                case "nand":
                    ra = args[1].replace(",", "")
                    rb = args[2].replace(",", "")
                    rc = args[3].replace(",", "")
                    binRA = reg_to_bits(ra)
                    binRB = reg_to_bits(rb)
                    binRC = reg_to_bits(rc)
                    out.write("00" + binRC + binRB + binRA + format(10, "05b") + "\n")

                case "nor":
                    ra = args[1].replace(",", "")
                    rb = args[2].replace(",", "")
                    rc = args[3].replace(",", "")
                    binRA = reg_to_bits(ra)
                    binRB = reg_to_bits(rb)
                    binRC = reg_to_bits(rc)
                    out.write("00" + binRC + binRB + binRA + format(11, "05b") + "\n")

                case "xor":
                    ra = args[1].replace(",", "")
                    rb = args[2].replace(",", "")
                    rc = args[3].replace(",", "")
                    binRA = reg_to_bits(ra)
                    binRB = reg_to_bits(rb)
                    binRC = reg_to_bits(rc)
                    out.write("00" + binRC + binRB + binRA + format(12, "05b") + "\n")

                case "beq" | "be":
                    ra = args[1].replace(",", "")
                    rb = args[2].replace(",", "")
                    rc = args[3].replace("(", "").replace(")", "")
                    binRA = reg_to_bits(ra)
                    binRB = reg_to_bits(rb)
                    binRC = reg_to_bits(rc)
                    out.write("00" + binRC + binRB + binRA + format(13, "05b") + "\n")

                case "bne":
                    ra = args[1].replace(",", "")
                    rb = args[2].replace(",", "")
                    rc = args[3].replace("(", "").replace(")", "")
                    binRA = reg_to_bits(ra)
                    binRB = reg_to_bits(rb)
                    binRC = reg_to_bits(rc)
                    out.write("00" + binRC + binRB + binRA + format(14, "05b") + "\n")

                case "blt":
                    ra = args[1].replace(",", "")
                    rb = args[2].replace(",", "")
                    rc = args[3].replace("(", "").replace(")", "")
                    binRA = reg_to_bits(ra)
                    binRB = reg_to_bits(rb)
                    binRC = reg_to_bits(rc)
                    out.write("00" + binRC + binRB + binRA + format(15, "05b") + "\n")

                case "bgt":
                    ra = args[1].replace(",", "")
                    rb = args[2].replace(",", "")
                    rc = args[3].replace("(", "").replace(")", "")
                    binRA = reg_to_bits(ra)
                    binRB = reg_to_bits(rb)
                    binRC = reg_to_bits(rc)
                    out.write("00" + binRC + binRB + binRA + format(16, "05b") + "\n")

                case "sl":
                    ra = args[1].replace(",", "")
                    rb = args[2].replace(",", "")
                    rc = args[3].replace(",", "")
                    binRA = reg_to_bits(ra)
                    binRB = reg_to_bits(rb)
                    binRC = reg_to_bits(rc)
                    out.write("00" + binRC + binRB + binRA + format(17, "05b") + "\n")

                case "sr":
                    ra = args[1].replace(",", "")
                    rb = args[2].replace(",", "")
                    rc = args[3].replace(",", "")
                    binRA = reg_to_bits(ra)
                    binRB = reg_to_bits(rb)
                    binRC = reg_to_bits(rc)
                    out.write("00" + binRC + binRB + binRA + format(18, "05b") + "\n")

                case "mv":
                    src = args[1].replace(",", "")
                    dst = args[2].replace(",", "")
                    binSRC = reg_to_bits(src)
                    binDST = reg_to_bits(dst)
                    out.write("00" + "000" + binSRC + binDST + format(21, "05b") + "\n")

                case "li":
                    if args[1].lstrip("-").isdigit():
                        value = int(args[1])
                        out.write(format(value, "011b") + format(19, "05b") + "\n")
                    else:
                        dest = args[1].replace(",", "")
                        value = int(args[2])
                        out.write(format(value, "011b") + format(19, "05b") + "\n")
                        binDST = reg_to_bits(dest)
                        out.write("00" + "000" + "001" + binDST + format(21, "05b") + "\n")

                case "jmp":
                    ra = reg_to_bits(args[1].replace(",", ""))
                    out.write("00000000" + ra + format(20, "05b") + "\n")

                case "ret":
                    out.write(format(23, "016b") + "\n")

                case "call":
                    ra = reg_to_bits(args[1].replace(",", ""))
                    out.write("00000000" + ra + format(22, "05b") + "\n")

                case _:
                    if len(line) == 16 and all(bit in "01" for bit in line):
                        out.write(line + "\n")
                    else:
                        print("Unknown instruction: " + line)

def send_uart_command(command, data):
    ser.write(b"@")
    echo = ser.read(1)
    if echo != b"@":
        print("Error: No start ack, got", echo, list(echo))
        return False

    ser.write(bytes([command]))
    ack_hi = ser.read(1)
    if ack_hi != b"!":
        print("Error: No Ack High, got", ack_hi, list(ack_hi))
        return False

    ser.write(bytes([data]))
    ack_lo = ser.read(1)
    if ack_lo != b"$":
        print("Error: No Ack Low, got", ack_lo, list(ack_lo))
        return False

    return True

print("Which COM port is the FPGA on? (number only) ")

for port in list_ports.comports():
    print(port.device, port.description)
port_number = 0

while True:
    text = input("Port Number: ")

    try:
        value = int(text)
        break
    except ValueError:
        print("enter a number")

port_number = value
try:
    ser = serial.Serial(port= "COM" + str(port_number), baudrate=115200, bytesize=8, parity="N", stopbits=1, timeout=1)
except serial.SerialException as e:
    print("Could not open port:", e)

ser.reset_input_buffer()
ser.reset_output_buffer()
while(True):
    argin =  input("Enter an Argument: ")
    argin =  argin.lower()
    args = argin.split()
    match args[0]:
        case "help":
            print("Args: " \
            "help, writereg [reg] [value], writemem [mem] [value], " \
            "readreg, readmem, " \
            "compile [name] [output], send [name]," \
            "halt, continue, step ")
        case "writereg":
            if len(args) < 3:
                            print("usage: writereg [reg] [value]")
                            continue

            print()
        case "writemem":
            if len(args) < 3:
                print("usage: writemem [mem] [value]")
                continue
            try:
                address = int(args[1], 0)
                value = int(args[2], 0)
            except ValueError:
                print("address and value must be numbers")
                continue
            if address < 0 or address > 0xB9AF or value < 0 or value > 0xFFFF:
                print("address must be 0..0xB9AF and value must be 0..0xFFFF")
                continue

            commands = [
                (0xD0, (address >> 8) & 0xFF),
                (0xC0, address & 0xFF),
                (0xF0, (value >> 8) & 0xFF),
                (0xE0, value & 0xFF),
                (0x60, 0x00),
            ]
            failed = False
            for command, data in commands:
                if not send_uart_command(command, data):
                    failed = True
                    break
            if not failed:
                print(f"Wrote 0x{value:04X} to 0x{address:04X}")
        case "readreg":
            if len(args) < 2:
                print("usage: readreg [reg]")
                continue
            try:
                register = int(args[1], 0)
            except ValueError:
                print("register must be a number from 0 to 7")
                continue
            if register < 0 or register > 7:
                print("register must be a number from 0 to 7")
                continue
            if not send_uart_command(register << 2, 0x00):
                continue
            data = ser.read(2)
            if len(data) != 2:
                print("Error: Timed out reading register data")
                continue
            value = int.from_bytes(data, "big")
            print(f"r{register}: 0x{value:04X} ({value})")
        case "readmem":
            if len(args) < 2:
                print("usage: readmem [mem]")
                continue
            try:
                address = int(args[1], 0)
            except ValueError:
                print("address must be a number")
                continue
            if address < 0 or address > 0xB9AF:
                print("address must be 0..0xB9AF")
                continue

            commands = [
                (0xD0, (address >> 8) & 0xFF),
                (0xC0, address & 0xFF),
                (0x20, 0x00),
            ]
            failed = False
            for command, data in commands:
                if not send_uart_command(command, data):
                    failed = True
                    break
            if failed:
                continue

            data = ser.read(2)
            if len(data) != 2:
                print("Error: Timed out reading memory data")
                continue
            value = int.from_bytes(data, "big")
            instruction = format(value, "016b")
            decoded = disassemble(instruction)
            if decoded not in ("invalid instruction", "unknown instruction"):
                print(f"0x{address:04X}: 0x{value:04X} ({decoded})")
            else:
                print(f"0x{address:04X}: 0x{value:04X} ({value})")
        case "compile":
            if len(args) < 3:
                print("usage: compile <input> <output>")
                continue
            assemble(args[1], args[2])
        case "send":
            if len(args) < 2:
                print("usage: send <name> [start_address]")
                continue
            try:
                start_address = int(args[2], 0) if len(args) >= 3 else 0
                with open(args[1], "r", encoding="utf-8") as source:
                    words = [line.strip() for line in source if line.strip() and not line.lstrip().startswith("#")]
            except (ValueError, OSError) as error:
                print("Could not read compiled instruction file:", error)
                continue
            if any(len(word) != 16 or any(bit not in "01" for bit in word) for word in words):
                print("send expects a compiled file with one 16-bit binary instruction per line")
                continue
            if start_address < 0 or start_address + len(words) > 0xB500:
                print("instruction range must fit in memory addresses 0..0xB4FF")
                continue

            failed = False
            for offset, word in enumerate(words):
                address = start_address + offset
                value = int(word, 2)
                print(f"addr=0x{address:04X} value=0x{value:04X}")
                commands = [
                    (0xD0, (address >> 8) & 0xFF),
                    (0xC0, address & 0xFF),
                    (0xF0, (value >> 8) & 0xFF),
                    (0xE0, value & 0xFF),
                    (0x60, 0x00),
                ]
                for command, data in commands:
                    if not send_uart_command(command, data):
                        failed = True
                        break
                if failed:
                    break
            if not failed:
                print(f"Sent {len(words)} instruction(s) starting at 0x{start_address:04X}")
        case "halt":
            if not send_uart_command(0x80, 0x00):
                continue
        case "run":
            if not send_uart_command(0xA0, 0x00):
                continue
        case "step":
            if not send_uart_command(0xB0, 0x00):
                continue
        case _:
            print("Unknown command: " + args[0] + " (type help for a list of commands)")

def bits_to_reg(bits):
    bits = bits.lower()
    if bits == "000":
        return "zero"
    elif bits == "001":
        return "r1"
    elif bits == "010":
        return "r2"
    elif bits == "011":
        return "r3"
    elif bits == "100":
        return "r4"
    elif bits == "101":
        return "r5"
    elif bits == "110":
        return "sp"
    elif bits == "111":
        return "ra"
    else:
        return "unknown"


def reg_to_bits(reg):
    reg = reg.lower()
    if reg == "zero" or reg == "r0":
        return "000"
    elif reg == "r1":
        return "001"
    elif reg == "r2":
        return "010"
    elif reg == "r3":
        return "011"
    elif reg == "r4":
        return "100"
    elif reg == "r5":
        return "101"
    elif reg == "sp" or reg == "r6":
        return "110"
    elif reg == "ra" or reg == "r7":
        return "111"
    else:
        return "000"


def disassemble(line):
    line = line.strip()
    if len(line) != 16:
        return "invalid instruction"

    opcode = line[-5:]
    op = int(opcode, 2)

    match op:
        case 0:
            rb = bits_to_reg(line[5:8])
            ra = bits_to_reg(line[8:11])
            return f"ld {ra}, ({rb})"
        case 1:
            rb = bits_to_reg(line[5:8])
            ra = bits_to_reg(line[8:11])
            return f"st {ra}, ({rb})"
        case 2:
            rc = bits_to_reg(line[2:5])
            rb = bits_to_reg(line[5:8])
            ra = bits_to_reg(line[8:11])
            return f"add {ra}, {rb}, {rc}"
        case 3:
            rc = bits_to_reg(line[2:5])
            rb = bits_to_reg(line[5:8])
            ra = bits_to_reg(line[8:11])
            return f"sub {ra}, {rb}, {rc}"
        case 4:
            rc = bits_to_reg(line[2:5])
            rb = bits_to_reg(line[5:8])
            ra = bits_to_reg(line[8:11])
            return f"mul {ra}, {rb}, {rc}"
        case 5:
            rc = bits_to_reg(line[2:5])
            rb = bits_to_reg(line[5:8])
            ra = bits_to_reg(line[8:11])
            return f"div {ra}, {rb}, {rc}"
        case 6:
            rc = bits_to_reg(line[2:5])
            rb = bits_to_reg(line[5:8])
            ra = bits_to_reg(line[8:11])
            return f"mod {ra}, {rb}, {rc}"
        case 7:
            rc = bits_to_reg(line[2:5])
            rb = bits_to_reg(line[5:8])
            ra = bits_to_reg(line[8:11])
            return f"and {ra}, {rb}, {rc}"
        case 8:
            rc = bits_to_reg(line[2:5])
            rb = bits_to_reg(line[5:8])
            ra = bits_to_reg(line[8:11])
            return f"or {ra}, {rb}, {rc}"
        case 9:
            rb = bits_to_reg(line[5:8])
            ra = bits_to_reg(line[8:11])
            return f"not {ra}, {rb}"
        case 10:
            rc = bits_to_reg(line[2:5])
            rb = bits_to_reg(line[5:8])
            ra = bits_to_reg(line[8:11])
            return f"nand {ra}, {rb}, {rc}"
        case 11:
            rc = bits_to_reg(line[2:5])
            rb = bits_to_reg(line[5:8])
            ra = bits_to_reg(line[8:11])
            return f"nor {ra}, {rb}, {rc}"
        case 12:
            rc = bits_to_reg(line[2:5])
            rb = bits_to_reg(line[5:8])
            ra = bits_to_reg(line[8:11])
            return f"xor {ra}, {rb}, {rc}"
        case 13:
            rc = bits_to_reg(line[2:5])
            rb = bits_to_reg(line[5:8])
            ra = bits_to_reg(line[8:11])
            return f"beq {ra}, {rb}, ({rc})"
        case 14:
            rc = bits_to_reg(line[2:5])
            rb = bits_to_reg(line[5:8])
            ra = bits_to_reg(line[8:11])
            return f"bne {ra}, {rb}, ({rc})"
        case 15:
            rc = bits_to_reg(line[2:5])
            rb = bits_to_reg(line[5:8])
            ra = bits_to_reg(line[8:11])
            return f"blt {ra}, {rb}, ({rc})"
        case 16:
            rc = bits_to_reg(line[2:5])
            rb = bits_to_reg(line[5:8])
            ra = bits_to_reg(line[8:11])
            return f"bgt {ra}, {rb}, ({rc})"
        case 17:
            rc = bits_to_reg(line[2:5])
            rb = bits_to_reg(line[5:8])
            ra = bits_to_reg(line[8:11])
            return f"sl {ra}, {rb}, {rc}"
        case 18:
            rc = bits_to_reg(line[2:5])
            rb = bits_to_reg(line[5:8])
            ra = bits_to_reg(line[8:11])
            return f"sr {ra}, {rb}, {rc}"
        case 19:
            immediate = int(line[:-5], 2)
            return f"li {immediate}"
        case 20:
            ra = bits_to_reg(line[8:11])
            return f"jmp {ra}"
        case 21:
            src = bits_to_reg(line[5:8])
            dst = bits_to_reg(line[8:11])
            return f"mv {src}, {dst}"
        case 22:
            ra = bits_to_reg(line[8:11])
            return f"call {ra}"
        case 23:
            return "ret"
        case _:
            return "unknown instruction"


def assemble(input_file, output_file):
    out = open(output_file, "w", encoding="utf-8")

    for line in input_file:
        line = line.strip()
        if not line or line.startswith("#"):
            continue

        args = line.split()
        match args[0].lower():
            case "ld":
                ra = args[1].replace(",", "")
                rb = args[2].replace("(", "").replace(")", "")
                binRA = reg_to_bits(ra)
                binRB = reg_to_bits(rb)
                out.write("00000" + binRB + binRA + format(0, "05b") + "\n")

            case "st":
                ra = args[1].replace(",", "")
                rb = args[2].replace("(", "").replace(")", "")
                binRA = reg_to_bits(ra)
                binRB = reg_to_bits(rb)
                out.write("00000" + binRB + binRA + format(1, "05b") + "\n")

            case "add":
                ra = args[1].replace(",", "")
                rb = args[2].replace(",", "")
                rc = args[3].replace(",", "")
                binRA = reg_to_bits(ra)
                binRB = reg_to_bits(rb)
                binRC = reg_to_bits(rc)
                out.write("00" + binRC + binRB + binRA + format(2, "05b") + "\n")

            case "sub":
                ra = args[1].replace(",", "")
                rb = args[2].replace(",", "")
                rc = args[3].replace(",", "")
                binRA = reg_to_bits(ra)
                binRB = reg_to_bits(rb)
                binRC = reg_to_bits(rc)
                out.write("00" + binRC + binRB + binRA + format(3, "05b") + "\n")

            case "mv":
                src = args[1].replace(",", "")
                dst = args[2].replace(",", "")
                binSRC = reg_to_bits(src)
                binDST = reg_to_bits(dst)
                out.write("00" + "000" + binSRC + binDST + format(21, "05b") + "\n")

            case "li":
                if args[1].lstrip("-").isdigit():
                    value = int(args[1])
                    out.write(format(value, "011b") + format(19, "05b") + "\n")
                else:
                    dest = args[1].replace(",", "")
                    value = int(args[2])
                    out.write(format(value, "011b") + format(19, "05b") + "\n")
                    binDST = reg_to_bits(dest)
                    out.write("00" + "000" + "001" + binDST + format(21, "05b") + "\n")

            case "ret":
                out.write(format(23, "016b") + "\n")

            case _:
                print("Unknown instruction: " + line)

    out.close()
