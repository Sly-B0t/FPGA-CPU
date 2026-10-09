    module top(input wire clk, input wire rx, output wire tx);
        wire [15:0] address;
        wire memread;
        wire memwrite;
        wire [15:0] memDataIn;
        wire [15:0] memDataOut;
        reg [7:0] tx_data;
        reg tx_start;
        wire [7:0] rx_data;
        wire rx_done;
        wire tx_busy;
        wire [15:0] regOut;
        reg [2:0] regIn;
        reg uartread;
        reg uartwrite;
        reg [15:0] uartaddress;
        reg [15:0] uartdataIn;
        wire [15:0] uartdataOut;
        reg [15:0] uart_read_data;
        reg [15:0] uart_write_data = 0;
        reg halt = 1;
        reg step = 0;
        Processor processor(clk, address,memread,memwrite,memDataIn,memDataOut, regOut, regIn, halt, step);
        Memory memory(address,memread,memwrite,memDataIn,clk,memDataOut, uartread,uartwrite,uartaddress,uartdataIn,uartdataOut);
        uart_RX uart_rx(clk, rx,rx_data,rx_done);
        uart_TX uart_tx(clk,tx, tx_data, tx_start,tx_busy);
        reg [3:0] cycle = 0;
        reg [2:0] uart_state = 0;
        reg [15:0] uart_instruction;    
        reg uart_recieved = 0;
        reg[15:0] uart_mem_reg = 0;
        always @(posedge clk) begin
            tx_start <= 0;
            uartread <= 0;
            uartwrite <= 0;
            step <= 0;
            if(rx_done && !tx_busy) begin
                case(uart_state)
                    0: begin
                        uart_recieved <= 0;
                        if(rx_data == "@") begin //check for start bit
                            tx_data <= rx_data; //echo start bit back
                            tx_start <= 1; //start transmission
                            uart_state <= 1;
                        end
                        else begin //recieved something other than start bit
                            tx_data <= "#";
                            tx_start <= 1;
                        end
                    end
                    1: begin
                        uart_instruction[15:8] <= rx_data;
                        tx_data <= "!";
                        tx_start <= 1;
                        uart_state <= 2;

                    end
                    2: begin 
                        uart_instruction[7:0] <= rx_data;
                        tx_data <= "$";
                        tx_start <= 1;
                        uart_state <= 0;
                        uart_recieved <= 1;

                    end
                endcase
            end
            if(uart_recieved == 1) begin 
                case(uart_instruction[15:13]) 
                3'b000: begin //read register
                    case(cycle)
                    0: begin
                        regIn <= uart_instruction[12:10];
                        cycle <= 1;
                    end

                    1: begin
                        uart_read_data <= regOut;
                        cycle <= 2;
                    end

                    2: begin
                        if(!tx_busy) begin
                            tx_data <= uart_read_data[15:8];
                            tx_start <= 1;
                            cycle <= 3;
                        end
                    end

                    3: begin
                        if(tx_busy) begin
                            cycle <= 4;
                        end
                    end

                    4: begin
                        if(!tx_busy) begin
                            tx_data <= uart_read_data[7:0];
                            tx_start <= 1;
                            cycle <= 5;
                        end
                    end

                    5: begin
                        if(tx_busy) begin
                            cycle <= 6;
                        end
                    end

                    6: begin
                        if(!tx_busy) begin
                            cycle <= 0;
                            uart_recieved <= 0;
                        end
                    end
                    endcase
                end
                3'b001: begin //read memory
                    case(cycle)
                    0: begin
                        uartaddress <= uart_mem_reg;
                        cycle <= 1;
                    end

                    1: begin
                        cycle <= 2;
                    end

                    2: begin
                        uartread <= 1;
                        cycle <= 3;
                    end

                    3: begin
                        uartread <= 1;
                        cycle <= 4;
                    end

                    4: begin
                        uartread <= 1;
                        cycle <= 5;
                    end

                    5: begin
                        cycle <= 6;
                    end

                    6: begin
                        uart_read_data <= uartdataOut;
                        cycle <= 7;
                    end

                    7: begin
                        if(!tx_busy) begin
                            tx_data <= uart_read_data[15:8];
                            tx_start <= 1;
                            cycle <= 8;
                        end
                    end

                    8: begin
                        if(tx_busy)
                            cycle <= 9;
                    end

                    9: begin
                        if(!tx_busy) begin
                            tx_data <= uart_read_data[7:0];
                            tx_start <= 1;
                            cycle <= 10;
                        end
                    end

                    10: begin
                        if(tx_busy)
                            cycle <= 11;
                    end

                    11: begin
                        if(!tx_busy) begin
                            cycle <= 0;
                            uart_recieved <= 0;
                        end
                    end
                    endcase
                end
                3'b010: begin //write register
                uart_recieved <= 0;
                end
                3'b011: begin //write memory
                    case(cycle)
                    0: begin
                        uartaddress <= uart_mem_reg;
                        uartdataIn <= uart_write_data;
                        cycle <= 1;
                    end

                    1: begin
                        uartwrite <= 1;
                        cycle <= 0;
                        uart_recieved <= 0;
                    end
                    endcase
                end
                3'b100: begin //halt
                    halt <= 1;
                    uart_recieved <= 0;
                end
                3'b101: begin //run/step
                    if(uart_instruction[12] ==  1'b1) begin 
                        step <= 1;
                    end
                    else begin 
                        halt <= 0;
                    end
                    uart_recieved <= 0;
                end
                3'b110: begin // set address high/low
                    if(uart_instruction[12] == 1'b1)
                        uart_mem_reg[15:8] <= uart_instruction[7:0];
                    else
                        uart_mem_reg[7:0] <= uart_instruction[7:0];

                    uart_recieved <= 0;
                end
                3'b111: begin // set write data high/low
                    if(uart_instruction[12] == 1'b1)
                        uart_write_data[15:8] <= uart_instruction[7:0];
                    else
                        uart_write_data[7:0] <= uart_instruction[7:0];

                    uart_recieved <= 0;
                end
                endcase
            end
        end
    endmodule
    /*
    UART CODES

    echo means start

    # means misunderstood command expected start bit

    ! is ack high

    $ is ack low

    */


    /*
    UART transmission for registers and halt/run/step is

    start byte || echo
    high byte || ACK high
    low byte || ACK low

    UART transmission for memory is 

    (specifying the instruction)
    start byte || echo
    high byte || ACK high
    low byte || ACK low

    setting memory is special, you have to set the reg youre gonna read/write to first with 0x7 for the top
    bits then using the last 
    */

    /* UART INSTRUCTION SET  (3 bits)    || note
    0x0: 0: read register       || uses uart mem reg
    0x1: 1: read memory         ||
    0x3: 2: write register (im not working on this right now just change te memory to set a register then move to that place in memory by changing pc)
    0x3: 3: write memory
    0x4: 4: halt
    0x5: 5: run                 || checks the bit after to see if its 1 to see to step or run indefinitely
    0x6: 6: set memreg  high     || sets bits 8-16
    0x7: 7: set memreg  low       || sets bits 1-8


    */



    /*
    0:load
    1:store
    2:add
    3:sub
    4:mul
    5:div
    6:mod
    7:and
    8:or
    9:not
    10:nand
    11:nor
    12:xor
    13:branch if equal (beq RC,RA, (RB)) RB is the destination
    14:branch if not equal
    15:branch if less than
    16:branch if greater than
    17:shift L
    18:shift R
    19:load immdiate
    20:jump (jump (rc)) jump to rc
    21:move
    22:call (call (ra)) basically jump but keep track of this position
    23:ret

    */
    module Processor(input wire clk,output reg [15:0] address, output reg memread, output reg memwrite,
    output reg [15:0] memDataIn, input wire [15:0] memDataOut, output wire[15:0] regOut, input wire [2:0] regIn, input wire halt, input wire stepin);
        reg [2:0] state = 0; // come back for the size
        reg [15:0] IR; // reg C, regB, reg A, op code; reg C = destination
        reg [15:0] regA;
        reg [15:0] regB;
        reg[2:0] regC;
        reg [15:0] PC = 0 ;
        reg zreg;
        reg nreg;
        reg flagwrite;
        reg [4:0] instruction;
        reg [15:0] registers [0:7];
        reg step = 0;
        assign regOut = registers[regIn];
        //only run on the clk high if we're not stopped or we're stepping
        always @ (posedge clk) begin
            step <= stepin;
            if(!halt || step) begin
                memread <= 0;
                memwrite <= 0;
                case (state)
                    0: begin
                        address <=  PC;
                        memread <= 1;
                        state <= 1;
                        PC <=  PC + 1;
                    end
                    1: begin 
                        state <= 2;
                    end
                    2: begin
                        IR <= memDataOut;
                        state <= 3;
                    end
                    3: begin
                        regA <= registers[IR[10:8]];
                        regB <= registers[IR[13:11]];
                        regC <= IR[7:5];
                        instruction <= IR[4:0];
                        state <= 4;
                    end
                    4:begin
                        case (instruction)
                            0: begin // load the address regA into regC
                                address <=  regA;
                                memread <= 1;
                                state <= 5;
                            end
                            1:begin //store reg C at address regA
                                address <= regA;
                                memwrite <= 1;
                                memDataIn <=  registers[regC];
                                state<=0;
                            end
                            2: begin // add regA and regB into IR
                                registers[regC] <= regA + regB;
                                zreg <= ((regA + regB) == 16'd0);
                                nreg <= (regA + regB) >> 15;
                                state<= 0;
                                step <= 0;
                            end
                            3: begin//sub
                                registers[regC] <= regA - regB;
                                zreg <= ((regA - regB) == 16'd0);
                                nreg <= (regA - regB) >> 15;
                                state<=0;
                                step <= 0;
                            end
                            4: begin//mul
                                registers[regC] <= regA * regB;
                                zreg <= ((regA * regB) == 16'd0);
                                nreg <= (regA * regB) >> 15;
                                state<=0;
                                step <= 0;
                            end
                            5: begin//div
                                registers[regC] <= regA / regB;
                                zreg <= ((regA / regB) == 16'd0);
                                nreg <= (regA / regB) >> 15;
                                state<=0;
                                step <= 0;
                            end
                            6: begin //mod
                                registers[regC] <= regA % regB;
                                zreg <= ((regA % regB) == 16'd0);
                                nreg <= (regA % regB) >> 15;
                                state<=0;
                                step <= 0;
                            end
                            7:begin// and
                                registers[regC] <= regA & regB;
                                zreg <= ((regA & regB) == 16'd0);
                                nreg <= (regA & regB) >> 15;
                                state<=0;
                                step <= 0;
                            end
                            8: begin //or
                                registers[regC] <= regA | regB;
                                zreg <= ((regA | regB) == 16'd0);
                                nreg <= (regA | regB) >> 15;
                                state<=0;
                                step <= 0;
                            end
                            9: begin //not
                                registers[regC] <= ~regA;
                                zreg <= (~(regA) == 16'd0);
                                nreg <= (~(regA)) >> 15;
                                state<=0;
                                step <= 0;
                            end
                            10: begin//NAND
                                registers[regC] <= ~(regA & regB);
                                zreg <= (~(regA & regB) == 16'd0);
                                nreg <= ~(regA & regB) >> 15;
                                state<=0;
                                step <= 0;
                            end
                            11:begin//NOR
                                registers[regC] <= ~(regA | regB);
                                zreg <= (~(regA | regB) == 16'd0);
                                nreg <= ~(regA | regB) >> 15;
                                state<=0;
                                step <= 0;
                            end
                            12: begin//XOR
                                registers[regC] <= (regA ^ regB);
                                zreg <= ((regA ^ regB) == 16'd0);
                                nreg <= (regA ^ regB) >> 15;
                                state<=0;
                                step <= 0;
                            end
                            13: begin //branch if equal
                                if (registers[regC]== regA) begin
                                    PC <= regB;
                                end
                                state<=0;
                                step <= 0;
                            end
                            14:begin // branch if not equal
                                if (registers[regC] != regA) begin
                                    PC <= regB;
                                end
                                state<=0;
                                step <= 0;
                            end
                            15: begin //branch if less than
                                if (registers[regC] < regA) begin
                                    PC <= regB;
                                end
                                state<=0;
                                step <= 0;
                            end
                            16:  begin //branch if greater than
                                if (registers[regC] > regA) begin
                                    PC <= regB;
                                end
                                state<=0;
                                step <= 0;
                            end
                            17: begin//shift L
                                registers[regC] <= (regA << regB);
                                zreg <= ((regA << regB) == 16'd0);
                                nreg <= (regA << regB) >> 15;
                                state<=0;
                                step <= 0;
                            end
                            18: begin//shift right
                                registers[regC] <= (regA >> regB);
                                zreg <= ((regA >> regB) == 16'd0);
                                nreg <= (regA >> regB) >> 15;
                                state<=0;
                                step <= 0;
                            end
                            19: begin //li into reg 1 due to limitations
                                registers[1] <= IR[15:5];
                                state<=0;
                                step <= 0;
                            end
                            20: begin// jump
                                PC <= registers[regC];
                                state<=0;
                                step <= 0;
                            end
                            21: begin//move
                                registers[regC] <= regA;
                                state<=0;
                                step <= 0;
                            end
                            22: begin//call 
                                registers[7] <= PC;
                                PC <= registers[regC];
                                state<=0;
                                step <= 0;
                            end
                            23: begin//ret
                                PC <= registers[7];
                                state<=0;
                                step <= 0;
                            end
                        endcase
                    end
                    5: begin
                        state <= 6;
                    end
                    6: begin
                        registers[regC] <= memDataOut;
                        state <= 0;
                        step <= 0;
                    end
            endcase
                registers[0] <= 0;
            end
        end
    endmodule




    module Memory(
        input wire [15:0] address,
        input wire memread,
        input wire memwrite,
        input wire [15:0] dataIn,
        input wire clk,
        output reg [15:0] dataOut,
        input wire uartread,
        input wire uartwrite,
        input wire [15:0] uartaddress,
        input wire [15:0] uartdataIn,
        output reg [15:0] uartdataOut
    );
        reg [15:0] mem [0:255];

        always @(posedge clk) begin
            if(memwrite) begin
                mem[address[7:0]] <= dataIn;
                dataOut <= dataIn;
            end
            else if(memread) begin
                dataOut <= mem[address[7:0]];
            end

            if(uartwrite) begin
                mem[uartaddress[7:0]] <= uartdataIn;
                uartdataOut <= uartdataIn;
            end
            else if(uartread) begin
                uartdataOut <= mem[uartaddress[7:0]];
            end
        end
    endmodule

    module uart_TX(input wire clk, output reg tx, input wire [7:0] tx_data, input wire tx_start, output wire tx_busy);
        reg [1:0] state = 0;
        reg [3:0] bit = 0;
        reg [8:0] counter = 0;
        reg waiting = 0;
        reg [7:0] tx_buffer;
        assign tx_busy = (state != 0);
        always @(posedge clk) begin 
            case(state)
                0: begin
                    tx <= 1;

                    if(tx_start) begin
                        state <= 1;
                        counter <= 0;
                        bit <= 0;
                        waiting <= 0;
                        tx_buffer <= tx_data;
                    end
                end
                1: begin 
                    tx <= 0;
                    if(counter == 233) begin 
                        state <= 2;
                        counter <= 0;
                    end
                    else begin
                        counter <= counter + 1;
                    end
                end
                2: begin
                    // set tx =  to the bit at tx_data then waiting. do that 8 times then stop
                    if(waiting == 0) begin 
                        tx <= tx_buffer[bit];
                        bit <= bit + 1;
                        waiting <= 1;
                    end
                    if(waiting == 1) begin 
                        if(counter == 233) begin 
                            if(bit == 8) begin 
                                state <= 3;
                                counter <= 0;
                                bit <= 0;
                            end
                            waiting <= 0;
                            counter <= 0;
                        end
                        else begin 
                            counter <= counter + 1;
                        end
                    end
                end
                3: begin
                    tx <= 1;

                    if(counter == 233) begin
                        state <= 0;
                        counter <= 0;
                    end
                    else begin
                        counter <= counter + 1;
                    end
                end
            endcase
        end
    endmodule

    module uart_RX(input wire clk, input wire rx, output reg [7:0] rx_data, output reg rx_done);
        //waiting for the rx to drop from HIGH to LOW then waiting a half cycle and confirm its still low
        //then waiting a whole cycle to get inside the middle of the data bit
        //sample that bit then waiting a cycle do it for 7 more times
        //done
        reg [7:0] rx_buffer = 0;
        reg [3:0] bit = 0;
        reg [3:0] state = 0;
        reg [8:0] counter = 0;
        reg waiting = 0;
        reg prevrx = 1;
        reg rx_sync1 = 1;
        reg rx_sync2 = 1;
        always @(posedge clk) begin
            rx_done<= 0;
            rx_sync1 <= rx;
            rx_sync2 <= rx_sync1;
            case(state)
                0: begin 
                    if(prevrx == 1 && rx_sync2 == 0) begin //if rx dropped from HIGH to LOW in state 0 start waitinging half
                        waiting<= 1;
                    end          
                    if(waiting == 1) begin 
                        if(counter == 116) begin //waitinging half cycle done
                            if(rx_sync2 == 0) begin 
                                state <= 1;
                                counter <= 0;
                                bit <= 0;
                            end
                            else begin //not actually a full timing of a start bit
                                counter<=0;
                                waiting<=0;
                            end
                            
                        end
                        else begin //if half cycle isnt done yet keep counting
                            counter <= counter + 1;
                        end
                    end    
                    prevrx <= rx_sync2;
                    
                end
                1: begin 
                    //set rx_data[bit] to rx every cycle and increment bit when bit is 8 go to the next stage
                    if(waiting == 0) begin
                        rx_buffer[bit] <= rx_sync2;
                        bit <= bit + 1;
                        waiting <= 1;
                    end
                    if(waiting == 1) begin //if waitinging
                        if(counter == 233) begin //if counter is complete
                            if(bit == 8) begin  //if bit is done going from 0 -> 7 data is complete
                                state <= 2;
                                counter <= 0;
                            end
                            waiting <= 0;
                            counter <= 0;
                        end
                        else begin //if counter isnt done continue counting
                            counter <= counter + 1;
                        end
                    end
                end
                2: begin
                    rx_data <= rx_buffer;
                    state <= 0;
                    rx_done <= 1;
                end
                3: begin 

                end
            endcase
        end
    endmodule