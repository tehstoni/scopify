import argparse
import ipaddress

def read_ip_file(filename):
    with open(filename, 'r') as file:
        return [line.strip() for line in file.readlines() if line.strip()]

def ip_range_to_networks(ip_range):
    start_ip, end_ip = ip_range.split('-')
    start_ip = ipaddress.ip_address(start_ip)
    end_ip = ipaddress.ip_address(end_ip)
    return [ipaddr for ipaddr in ipaddress.summarize_address_range(start_ip, end_ip)]

def convert_to_networks(ip_list):
    networks = []
    for ip in ip_list:
        if '-' in ip:
            networks.extend(ip_range_to_networks(ip))
        else:
            networks.append(ipaddress.ip_network(ip, strict=False))
    return networks

def exclude_out_scope(in_scope, out_scope):
    excluded_networks = []
    for in_net in in_scope:
        if not any(in_net.overlaps(out_net) for out_net in out_scope):
            excluded_networks.append(in_net)
    return excluded_networks

def write_output(filename, networks):
    with open(filename, 'w') as file:
        for net in networks:
            file.write(str(net) + '\n')

def main():
    parser = argparse.ArgumentParser(description='Consolidate IP ranges while excluding certain IPs.')
    parser.add_argument('in_scope_file', help='File containing in-scope IP ranges')
    parser.add_argument('out_scope_file', help='File containing out-of-scope IP ranges')
    parser.add_argument('output_file', help='Output file name for the consolidated IP ranges')
    
    args = parser.parse_args()

    in_scope_ips = read_ip_file(args.in_scope_file)
    out_scope_ips = read_ip_file(args.out_scope_file)

    in_scope_networks = convert_to_networks(in_scope_ips)
    out_scope_networks = convert_to_networks(out_scope_ips)

    final_networks = exclude_out_scope(in_scope_networks, out_scope_networks)

    write_output(args.output_file, final_networks)
    print(f'Output written to {args.output_file}')

if __name__ == '__main__':
    main()
