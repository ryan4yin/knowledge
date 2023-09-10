module top_module(
    input [31:0] a,
    input [31:0] b,
    output [31:0] sum
);
    wire [15:0] sum_lo, sum_hi0, sum_hi1;
    wire cout0, cout1, cout2;
    
    add16 a_lo (a[15:0], b[15:0], 0, sum_lo, cout0);
    add16 a_hi0 (a[31:16], b[31:16], 0, sum_hi0, cout1);
    add16 a_hi1 (a[31:16], b[31:16], 1, sum_hi1, cout2);
    always @(*)
        case (cout0)
            0:  sum = {sum_hi0, sum_lo};
            1:  sum = {sum_hi1, sum_lo};
        endcase
  
endmodule
