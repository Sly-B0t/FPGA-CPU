# FPGA-CPU

16 bit Custom designed Cpu designed for the Tang nano 9k.

## Instruction Set

| Opcode | Instruction |
|---|---|
| #0 | ld => load |
| #1 | st => store |
| #2 | add |
| #3 | sub |
| #4 | mul |
| #5 | div |
| #6 | mod |
| #7 | and |
| #8 | or |
| #9 | not |
| #10 | nand |
| #11 | nor |
| #12 | xor |
| #13 | be => branch if equal (beq RC,RA, (RB)) RB is the destination |
| #14 | bne => branch if not equal |
| #15 | blt => branch if less than |
| #16 | bgt => branch if greater than |
| #17 | sl => shift L |
| #18 | sr => shift R |
| #19 | li => load immdiate into r1 |
| #20 | jmp => jump (jump (rc)) jump to rc |
| #21 | mv => move |
| #22 | call (call (ra)) basically jump but keep track of this position |
| #23 | ret |

## Registers

| Register | Name |
|---|---|
| 0 | zero (always holds zero) => zero // Restricted |
| 1 | load reg => r1// Restricted |
| 2 | argument 0 / return value => r2 |
| 3 | argument 1 => r3 |
| 4 | temporary => r4 |
| 5 | temporary => r5 |
| 6 | stack pointer (uninitialized by default) => sp //not restricted but important to use safely |
| 7 | return address => ra //restricted |

## Important Note

important note li DOES NOT TAKE a register as an argument  
it always sets reg 1 to the value  
so li 1 => r1 = 1  
then you can move r1 into r2

## Usage

To use this on your tang nano 9k upload this and program it with embedded flash mode
then use the python file to communicate with it over the COM ports. create your own assembly and compile then send it over with the commands below.

## UART INSTRUCTION SET

```text
/* UART INSTRUCTION SET  (3 bits)

#0x0: 0: read register
#0x1: 1: read memory
#0x3: 2: write register (im not working on this right now just change te memory to set a register then move to that place in memory by changing pc)
#0x3: 3: write memory
#0x4: 4: halt
#0x5: 5: run
#0x6: 6: set memreg  high
#0x7: 7: set memreg  low
*/