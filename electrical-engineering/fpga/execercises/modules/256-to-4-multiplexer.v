
module top_module( 
    input [1023:0] in,
    input [7:0] sel,
    output [3:0] out );
    always @(*) begin
        out = 0;
        for (int i = 0; i < 256; i += 1) begin
            if (sel == i) begin
                // start from `i * 4 + 3`, take the lower 4 bits.
                // You CAN NOT use in[i * 4 + 3 : i * 4] here, because Verilog does not allow variables on the right hand side of the bit selection in the array.
                out = in[i * 4 + 3 -:4];
            end
        end
    end
endmodule

