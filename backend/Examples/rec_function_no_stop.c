int rec(int i) {

    return rec( i- 1);
}


int main() {
    rec(5);
}