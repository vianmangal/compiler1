int sum_squares(int limit) {
    int total = 0;
    for (int index = 0; index < limit; index++) {
        total += index * index;
    }
    return total;
}

int main(void) {
    return sum_squares(10);
}
