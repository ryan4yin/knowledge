
// synthesis verilog_input_version verilog_2001
module top_module (
    input [7:0] in,
    output reg [2:0] pos );

    always @ (*) begin
        if (in & 8'b1) pos = 3'd0;
        else if (in & 8'b10) pos = 3'd1;
        else if (in & 8'b100) pos = 3'd2;
        else if (in & 8'b1000) pos = 3'd3;
        else if (in & 8'b10000) pos = 3'd4;
        else if (in & 8'b100000) pos = 3'd5;
        else if (in & 8'b1000000) pos = 3'd6;
        else if (in & 8'b10000000) pos = 3'd7;
        else pos = 3'd0;
    end


endmodule
