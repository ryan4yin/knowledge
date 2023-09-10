
module top_module(
    input [31:0] a,
    input [31:0] b,
    input sub,
    output [31:0] sum
);
    wire [15:0] sum_lo, sum_hi;
    wire cout0, cout1;
    wire[31:0] b2;
    assign b2 = {32{sub}} ^ b;
    
    add16 a_lo (a[15:0], b2[15:0], sub, sum_lo, cout0);
    add16 a_hi0 (a[31:16], b2[31:16], cout0, sum_hi, cout1);
    
    assign sum = {sum_hi, sum_lo};
endmodule
